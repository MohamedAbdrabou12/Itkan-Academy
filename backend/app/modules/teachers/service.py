# backend/app/modules/teachers/service.py
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.teachers.models import Teacher
from app.modules.teachers.schemas import TeacherCreate, TeacherUpdate
from app.modules.teachers.crud import teacher_crud
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import (
    UserCreate as UserCreateSchema,
    UserUpdate,
    UserRead,
)
from app.modules.users.crud import user_crud
from app.modules.classes.models import Class
from app.modules.roles.models import Role
from app.services.notification_service.workrs.worker import send_notification_task
from app.modules.users.schemas import BranchInfo


class TeacherService:
    @staticmethod
    async def _serialize_teacher(teacher: Teacher) -> Dict:
        user: User | None = getattr(teacher, "user", None)

        if user is None:
            raise HTTPException(status_code=404, detail="Linked user not found")
        
        user_data = UserRead(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            role_name=user.role_name,
            login_identifier=user.login_identifier,
            login_type=user.login_type,
            last_login=user.last_login,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
            branch_ids=[link.branch_id for link in user.branch_links]
            if user.branch_links
            else None,
            branches=[BranchInfo.from_orm(link.branch) for link in user.branch_links]
            if user.branch_links
            else None,
        )
        class_ids = (
            [c.id for c in getattr(teacher, "classes", [])] if teacher.classes else []
        )
        return {
            **user_data.model_dump(),
            "qualification": teacher.qualification,
            "specialization": teacher.specialization,
            "hire_date": teacher.hire_date,
            "employment_type": teacher.employment_type.value
            if teacher.employment_type
            else None,
            "class_ids": class_ids if class_ids else None,
        }

    @staticmethod
    async def list_teachers(
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[Dict]:
        teachers = await teacher_crud.get_all(db, search, sort_by, sort_order)
        return teachers

    @staticmethod
    async def get_teacher(db: AsyncSession, teacher_id: int) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="المعلم غير موجود")
        if not teacher.user:
            teacher.user = await db.get(User, teacher.user_id)
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def create_teacher(
        db: AsyncSession, teacher_in: TeacherCreate, creator: Optional[User] = None
    ):
        existing = await user_crud.get_by_email(db, teacher_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="هذا البريد مستخدم بالفعل")

        # Validate branch_ids
        if not teacher_in.branch_ids or len(teacher_in.branch_ids) == 0:
            raise HTTPException(
                status_code=400, detail="يجب ان تضيف المعلم على فرع واحد على الاقل"
            )

        # If creator is not admin, enforce branch restriction
        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if getattr(creator, "branch_ids", []) and not all(
                bid in getattr(creator, "branch_ids", [])
                for bid in teacher_in.branch_ids
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="انت غير مسجل على الفرع الذى تحاول الاضافة فيه",
                )

        # Validate classes
        class_objs = []
        if teacher_in.class_ids:
            for cid in teacher_in.class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                # Each class must belong to at least one of the teacher's branches
                if cls.branch_id not in teacher_in.branch_ids:
                    raise HTTPException(
                        status_code=400,
                        detail="لا يوجد فصل بهاذا الاسم على الفرع المحددة",
                    )
                class_objs.append(cls)

        # Create User
        role_res = await db.execute(select(Role).where(Role.name.ilike("teacher")))
        teacher_role = role_res.scalar_one_or_none()
        role_id = teacher_role.id if teacher_role else None

        user_payload = UserCreateSchema(
            full_name=teacher_in.full_name,
            email=teacher_in.email,
            phone=teacher_in.phone,
            role_id=role_id,
            login_identifier=teacher_in.email,
            login_type="email",
            branch_ids=teacher_in.branch_ids,  # allow multiple branches
            status=UserStatus.pending,
        )
        user = await user_crud.create(db, user_payload)

        # Save branch_ids in a many-to-many relation (user_branches)
        if teacher_in.branch_ids:
            await user_crud.assign_branches(db, user, teacher_in.branch_ids)

        teacher_payload = {
            "user_id": user.id,
            "qualification": teacher_in.qualification,
            "specialization": teacher_in.specialization,
            "hire_date": teacher_in.hire_date,
            "employment_type": teacher_in.employment_type,
        }
        teacher = await teacher_crud.create(db, teacher_payload)

        if class_objs:
            teacher.classes = class_objs
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)

        # Notify HR/admin
        await TeacherService._notify_hr_new_teacher(db, teacher, creator)

    @staticmethod
    async def update_teacher(
        db: AsyncSession, teacher_id: int, teacher_in: TeacherUpdate
    ) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="المعلم غير موجود")

        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="المستخدم المرتبط غير موجود")

        data = teacher_in.dict(exclude_unset=True)
        user_fields = {
            f: data.pop(f)
            for f in ("full_name", "email", "phone", "branch_ids")
            if f in data
        }

        if user_fields:
            if "email" in user_fields and user_fields["email"] != user.email:
                exist = await user_crud.get_by_email(db, user_fields["email"])
                if exist:
                    raise HTTPException(
                        status_code=400, detail="هذا البريد مستخدم بالفعل"
                    )
            await user_crud.update(db, user, UserUpdate(**user_fields))

            # Update branches if provided
            if "branch_ids" in user_fields:
                await user_crud.assign_branches(db, user, user_fields["branch_ids"])

        class_ids = data.pop("class_ids", None)
        if data:
            teacher = await teacher_crud.update(db, teacher, data)

        if class_ids is not None:
            teacher.classes = [
                await db.get(Class, cid)
                for cid in class_ids
                if await db.get(Class, cid)
            ]
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)

        teacher.user = await db.get(User, teacher.user_id)
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def delete_teacher(db: AsyncSession, teacher_id: int) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="المعلم غير موجود")
        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="المستخدم المرتبط غير موجود")

        user.status = UserStatus.deactive.value
        db.add(user)
        await db.commit()
        await db.refresh(teacher)

        teacher.user = user
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def approve_teacher(
        db: AsyncSession, teacher_id: int, approver: Optional[User] = None
    ) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="المعلم غير موجود")
        user = await db.get(User, teacher.user_id)
        user.status = UserStatus.active.value
        db.add(user)
        await db.commit()

        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="teacher_approved",
                payload={
                    "teacher_id": teacher.id,
                    "teacher_name": user.full_name,
                    "approved_by": approver.full_name if approver else "System",
                },
            )
        except Exception:
            pass

        teacher.user = user
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def reject_teacher(
        db: AsyncSession, teacher_id: int, approver: Optional[User] = None
    ) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="المعلم غير موجود")
        user = await db.get(User, teacher.user_id)
        user.status = UserStatus.rejected.value
        db.add(user)
        await db.commit()

        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="teacher_rejected",
                payload={
                    "teacher_id": teacher.id,
                    "teacher_name": user.full_name,
                    "rejected_by": approver.full_name if approver else "System",
                },
            )
        except Exception:
            pass

        teacher.user = user
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def _notify_hr_new_teacher(
        db: AsyncSession, teacher: Teacher, creator: Optional[User] = None
    ):
        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        admin_role = role_res.scalar_one_or_none()
        if not admin_role:
            return

        res = await db.execute(select(User).where(User.role_id == admin_role.id))
        admins = res.scalars().all()
        if not admins:
            return

        payload = {
            "teacher_id": teacher.id,
            "teacher_name": teacher.user.full_name if teacher.user else "Unknown",
            "created_by": creator.full_name if creator else "System",
        }
        for admin in admins:
            try:
                send_notification_task.delay(
                    user_id=str(admin.id),
                    channel="web",
                    template_type="new_teacher_pending",
                    payload=payload,
                )
            except Exception:
                pass
