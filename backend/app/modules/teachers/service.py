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
        user: User = getattr(teacher, "user", None)
        user_data = UserRead(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            role_id=user.role_id,
            role_name=user.role_name,
            branch_name=user.branch_name,
            permission_code=user.role.permission_links if user.role else None,
            status=user.status,
            last_login=user.last_login,
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
    async def list_teachers(db: AsyncSession) -> List[Dict]:
        teachers = await teacher_crud.get_all(db)
        return [await TeacherService._serialize_teacher(t) for t in teachers]

    @staticmethod
    async def get_teacher(db: AsyncSession, teacher_id: int) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        if not teacher.user:
            teacher.user = await db.get(User, teacher.user_id)
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def create_teacher(
        db: AsyncSession, teacher_in: TeacherCreate, creator: Optional[User] = None
    ) -> Dict:
        existing = await user_crud.get_by_email(db, teacher_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Validate branch_ids
        if not teacher_in.branch_ids or len(teacher_in.branch_ids) == 0:
            raise HTTPException(
                status_code=400, detail="Teacher must belong to at least one branch"
            )

        # If creator is not admin, enforce branch restriction
        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if not all(
                bid in getattr(creator, "branch_ids", [])
                for bid in teacher_in.branch_ids
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Teacher branches must match creator's branches",
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
                        detail=f"Class {cid} does not belong to the teacher's branches",
                    )
                class_objs.append(cls)

        # Create User
        role_res = await db.execute(select(Role).where(Role.name.ilike("teacher")))
        teacher_role = role_res.scalar_one_or_none()
        role_id = teacher_role.id if teacher_role else None

        # For simplicity, assign the first branch as user's primary branch
        primary_branch_id = teacher_in.branch_ids[0]

        user_payload = UserCreateSchema(
            name=teacher_in.name,
            email=teacher_in.email,
            phone=teacher_in.phone,
            role_id=role_id,
            branch_id=primary_branch_id,
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
        teacher.user = user
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def update_teacher(
        db: AsyncSession, teacher_id: int, teacher_in: TeacherUpdate
    ) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")

        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        data = teacher_in.dict(exclude_unset=True)
        user_fields = {
            f: data.pop(f)
            for f in ("name", "email", "phone", "branch_ids")
            if f in data
        }

        if user_fields:
            if "email" in user_fields and user_fields["email"] != user.email:
                exist = await user_crud.get_by_email(db, user_fields["email"])
                if exist:
                    raise HTTPException(
                        status_code=400, detail="Email already registered"
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
            raise HTTPException(status_code=404, detail="Teacher not found")
        user = await db.get(User, teacher.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

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
            raise HTTPException(status_code=404, detail="Teacher not found")
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
                    "teacher_name": user.name,
                    "approved_by": approver.name if approver else "System",
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
            raise HTTPException(status_code=404, detail="Teacher not found")
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
                    "teacher_name": user.name,
                    "rejected_by": approver.name if approver else "System",
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
            "teacher_name": teacher.user.name if teacher.user else "Unknown",
            "created_by": creator.name if creator else "System",
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
