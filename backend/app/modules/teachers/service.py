# backend/app/modules/teachers/service.py
from datetime import datetime  # noqa
from typing import List, Optional, Dict
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.teachers.models import Teacher
from app.modules.teachers.schemas import TeacherCreate, TeacherUpdate
from app.modules.teachers.crud import teacher_crud
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import UserCreate as UserCreateSchema, UserUpdate
from app.modules.users.crud import user_crud
from app.modules.classes.models import Class
from app.modules.roles.models import Role
from app.services.notification_service.workrs.worker import send_notification_task


class TeacherService:
    @staticmethod
    async def _serialize_teacher(teacher: Teacher) -> Dict:
        user = getattr(teacher, "user", None)
        class_ids = (
            [c.id for c in getattr(teacher, "classes", [])] if teacher.classes else []
        )
        return {
            "id": teacher.id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "branch_id": user.branch_id if user else None,
            "role_id": user.role_id if user else None,
            "status": user.status if user else None,
            "qualification": teacher.qualification,
            "specialization": teacher.specialization,
            "hire_date": teacher.hire_date,
            "employment_type": teacher.employment_type.value
            if teacher.employment_type
            else None,
            "class_ids": class_ids,
            "created_at": teacher.created_at,
            "updated_at": teacher.updated_at,
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
        # check if email already exists
        existing = await user_crud.get_by_email(db, teacher_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # branch validation for non-admin creator
        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if teacher_in.branch_id != creator.branch_id:
                raise HTTPException(
                    status_code=400, detail="branch_id must match creator's branch"
                )

        # class validation
        class_objs = []
        if teacher_in.class_ids:
            for cid in teacher_in.class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                if cls.branch_id != teacher_in.branch_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"class {cid} does not belong to provided branch",
                    )
                class_objs.append(cls)

        # get teacher role
        role_res = await db.execute(select(Role).where(Role.name.ilike("teacher")))
        teacher_role = role_res.scalar_one_or_none()
        role_id = teacher_role.id if teacher_role else None

        # teacher user payload
        user_payload = UserCreateSchema(
            name=teacher_in.name,
            email=teacher_in.email,
            phone=teacher_in.phone,
            role_id=role_id,
            branch_id=teacher_in.branch_id,
            status=UserStatus.pending,
        )
        user = await user_crud.create(db, user_payload)

        # teacher payload
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
            f: data.pop(f) for f in ("name", "email", "phone", "branch_id") if f in data
        }
        if user_fields:
            if "email" in user_fields and user_fields["email"] != user.email:
                exist = await user_crud.get_by_email(db, user_fields["email"])
                if exist:
                    raise HTTPException(
                        status_code=400, detail="Email already registered"
                    )
            await user_crud.update(db, user, UserUpdate(**user_fields))

        class_ids = data.pop("class_ids", None)
        if data:
            teacher = await teacher_crud.update(db, teacher, data)

        if class_ids is not None:
            class_objs = []
            for cid in class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                if cls.branch_id != user.branch_id:
                    raise HTTPException(
                        status_code=400, detail=f"class {cid} not in current branch"
                    )
                class_objs.append(cls)
            teacher.classes = class_objs
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
        teacher = await teacher_crud.approve(db, teacher)

        payload = {
            "teacher_id": teacher.id,
            "teacher_name": teacher.user.name,
            "approved_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(teacher.user.id),
                channel="web",
                template_type="teacher_approved",
                payload=payload,
            )
        except Exception:
            pass
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def reject_teacher(
        db: AsyncSession, teacher_id: int, approver: Optional[User] = None
    ) -> Dict:
        teacher = await teacher_crud.get_by_id(db, teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        teacher = await teacher_crud.reject(db, teacher)

        payload = {
            "teacher_id": teacher.id,
            "teacher_name": teacher.user.name,
            "rejected_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(teacher.user.id),
                channel="web",
                template_type="teacher_rejected",
                payload=payload,
            )
        except Exception:
            pass
        return await TeacherService._serialize_teacher(teacher)

    @staticmethod
    async def _notify_hr_new_teacher(
        db: AsyncSession, teacher: Teacher, creator: Optional[User] = None
    ):
        from app.modules.roles.models import Role
        from app.modules.users.models import User as UserModel

        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        admin_role = role_res.scalar_one_or_none()
        if not admin_role:
            return

        res = await db.execute(
            select(UserModel).where(UserModel.role_id == admin_role.id)
        )
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
