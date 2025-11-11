# backend/app/modules/students/service.py
from datetime import datetime  # noqa
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreate, StudentUpdate
from app.modules.students.crud import student_crud
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import UserCreate as UserCreateSchema, UserUpdate
from app.modules.users.crud import user_crud
from app.services.notification_service.workrs.worker import send_notification_task
from app.modules.classes.models import Class
from app.modules.roles.models import Role


class StudentService:
    @staticmethod
    async def _serialize_student(student: Student) -> Dict:
        user = getattr(student, "user", None)
        class_ids = (
            [c.id for c in getattr(student, "classes", [])]
            if getattr(student, "classes", None)
            else []
        )
        return {
            "id": student.id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "role_id": user.role_id if user else None,
            "branch_id": user.branch_id if user else None,
            "status": user.status if user else None,
            "parent_name": student.parent_name,
            "class_ids": class_ids,
            "admission_date": student.admission_date,
            "curriculum_progress": student.curriculum_progress,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
        }

    @staticmethod
    async def list_students(
        db: AsyncSession, status: Optional[str] = None
    ) -> List[Dict]:
        students = await student_crud.get_all(db, status)
        return [await StudentService._serialize_student(s) for s in students]

    @staticmethod
    async def get_student(db: AsyncSession, student_id: int) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        if not getattr(student, "user", None):
            student.user = await db.get(User, student.user_id)
        return await StudentService._serialize_student(student)

    @staticmethod
    async def create_student(
        db: AsyncSession, student_in: StudentCreate, creator: Optional[User] = None
    ) -> Dict:
        existing = await user_crud.get_by_email(db, student_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if (
                student_in.branch_id is None
                or student_in.branch_id != creator.branch_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="branch_id must match creator's branch",
                )

        class_objs = []
        if student_in.class_ids:
            for cid in student_in.class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                if cls.branch_id != student_in.branch_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"class {cid} does not belong to the provided branch",
                    )
                class_objs.append(cls)

        role_res = await db.execute(select(Role).where(Role.name.ilike("student")))
        student_role = role_res.scalar_one_or_none()
        role_id = student_role.id if student_role else None

        user_payload = UserCreateSchema(
            name=student_in.name,
            email=student_in.email,
            phone=student_in.phone,
            role_id=role_id,
            branch_id=student_in.branch_id,
            status=UserStatus.pending,
        )
        user = await user_crud.create(db, user_payload)

        student_payload = {
            "user_id": user.id,
            "parent_name": student_in.parent_name,
            "admission_date": student_in.admission_date,
            "curriculum_progress": student_in.curriculum_progress,
        }
        student = await student_crud.create(db, student_payload)

        if class_objs:
            student.classes = class_objs
            db.add(student)
            await db.commit()
            await db.refresh(student)

        await StudentService._notify_hr_new_student(db, student, creator)

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def update_student(
        db: AsyncSession, student_id: int, student_in: StudentUpdate
    ) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        data = student_in.dict(exclude_unset=True)

        user_fields = {}
        for f in ("name", "email", "phone", "branch_id"):
            if f in data:
                user_fields[f] = data.pop(f)
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
            student = await student_crud.update(db, student, data)

        if class_ids is not None:
            class_objs = []
            for cid in class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                if cls.branch_id != (user.branch_id if user else None):
                    raise HTTPException(
                        status_code=400, detail=f"class {cid} not in current branch"
                    )
                class_objs.append(cls)
            # Use crud helper to update join table
            await student_crud.update_student_classes(db, student, class_ids)
            # refresh relations
            await db.refresh(student)
            student.classes = class_objs
            db.add(student)
            await db.commit()
            await db.refresh(student)

        student.user = await db.get(User, student.user_id)
        return await StudentService._serialize_student(student)

    @staticmethod
    async def delete_student(db: AsyncSession, student_id: int) -> dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        attendance_exists = bool(student.attendance_records)
        payment_exists = bool(student.invoices)
        if attendance_exists or payment_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete student with attendance or payments",
            )

        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        user.status = UserStatus.deactive.value
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await db.refresh(student)

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def approve_student(
        db: AsyncSession, student_id: int, approver: Optional[User] = None
    ) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        user.status = UserStatus.active.value
        db.add(user)
        await db.commit()
        await db.refresh(student)

        payload = {
            "student_id": student.id,
            "student_name": user.name,
            "approved_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="student_approved",
                payload=payload,
            )
        except Exception:
            pass

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def reject_student(
        db: AsyncSession, student_id: int, approver: Optional[User] = None
    ) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        user.status = UserStatus.rejected.value
        db.add(user)
        await db.commit()

        payload = {
            "student_id": student.id,
            "student_name": user.name,
            "rejected_by": approver.name if approver else "System",
        }
        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="student_rejected",
                payload=payload,
            )
        except Exception:
            pass

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def _notify_hr_new_student(
        db: AsyncSession, student: Student, creator: Optional[User] = None
    ):
        from app.modules.roles.models import Role
        from app.modules.users.models import User as UserModel

        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        hr_role = role_res.scalar_one_or_none()
        if not hr_role:
            return

        res = await db.execute(select(UserModel).where(UserModel.role_id == hr_role.id))
        hr_users = res.scalars().all()
        if not hr_users:
            return

        payload = {
            "student_id": student.id,
            "student_name": creator.name
            if creator
            else (student.user.name if getattr(student, "user", None) else "Unknown"),
            "created_by": creator.name if creator else "System",
        }

        for hr in hr_users:
            try:
                send_notification_task.delay(
                    user_id=str(hr.id),
                    channel="web",
                    template_type="new_student_pending",
                    payload=payload,
                )
            except Exception:
                pass
