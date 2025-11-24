# backend/app/modules/students/service.py
from datetime import datetime  # noqa
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreate, StudentUpdate
from app.modules.students.crud import student_crud
from app.modules.users.models import User, UserStatus
from app.modules.users.schemas import UserCreate as UserCreateSchema, UserUpdate
from app.modules.users.crud import user_crud
from app.services.notification_service.workrs.worker import send_notification_task
from app.modules.classes.models import Class
from app.modules.roles.models import Role
from app.modules.users.schemas import BranchInfo
from app.modules.users.schemas import UserRead


class StudentService:
    @staticmethod
    async def _serialize_student(student: "Student") -> Dict:
        user: User = getattr(student, "user", None)

        user_data = UserRead(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            # phone=user.phone if user.phone and user.phone.isdigit() else None,
            phone=user.phone,
            role_id=user.role_id,
            role_name=user.role_name,
            branch_name=user.branch_name,
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
            [c.id for c in getattr(student, "classes", [])]
            if getattr(student, "classes", None)
            else []
        )

        return {
            **user_data.model_dump(),
            "class_ids": class_ids if class_ids else None,
            "admission_date": student.admission_date,
            "curriculum_progress": student.curriculum_progress,
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
            creator_branches = getattr(creator, "branch_ids", []) or []
            student_branches = student_in.branch_ids or []
            if not any(b in creator_branches for b in student_branches):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Student branches must match creator's branches",
                )

        # Validate class-branch match
        class_objs = []
        if student_in.class_ids:
            for cid in student_in.class_ids:
                cls = await db.get(Class, cid)
                if not cls:
                    raise HTTPException(
                        status_code=404, detail=f"Class {cid} not found"
                    )
                if cls.branch_id not in (student_in.branch_ids or []):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"class {cid} does not belong to provided branches",
                    )
                class_objs.append(cls)

        role_res = await db.execute(select(Role).where(Role.name.ilike("student")))
        student_role = role_res.scalar_one_or_none()
        role_id = student_role.id if student_role else None

        user_payload = UserCreateSchema(
            full_name=student_in.full_name,
            email=student_in.email,
            phone=student_in.phone,
            role_id=role_id,
            branch_ids=student_in.branch_ids,
            status=UserStatus.pending,
        )
        user = await user_crud.create(db, user_payload)

        student_payload = {
            "user_id": user.id,
            "admission_date": student_in.admission_date,
            "curriculum_progress": student_in.curriculum_progress,
        }
        student = await student_crud.create(db, student_payload)

        if class_objs:
            student.classes = class_objs
            db.add(student)
            await db.commit()
            await db.refresh(student)

        # 🔹 Reload full student with relations
        result = await db.execute(
            select(Student)
            .options(
                selectinload(Student.user).selectinload(User.branches),
                selectinload(Student.classes),
            )
            .where(Student.id == student.id)
        )
        student = result.scalar_one()

        await StudentService._notify_hr_new_student(db, student, creator)

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
                        status_code=400, detail="Email already registered"
                    )
            await user_crud.update(db, user, UserUpdate(**user_fields))

        class_ids = data.pop("class_ids", None)
        if data:
            student = await student_crud.update(db, student, data)

        if class_ids is not None:
            await student_crud.update_student_classes(db, student, class_ids)

        # Reload updated record
        result = await db.execute(
            select(Student)
            .options(
                selectinload(Student.user).selectinload(User.branches),
                selectinload(Student.classes),
            )
            .where(Student.id == student.id)
        )
        student = result.scalar_one()

        return await StudentService._serialize_student(student)

    @staticmethod
    async def delete_student(db: AsyncSession, student_id: int) -> dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        attendance_exists = bool(getattr(student, "attendance_records", []))
        payment_exists = bool(getattr(student, "invoices", []))
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

        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="student_approved",
                payload={
                    "student_id": student.id,
                    "student_name": user.full_name,
                    "approved_by": approver.full_name if approver else "System",
                },
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

        try:
            send_notification_task.delay(
                user_id=str(user.id),
                channel="web",
                template_type="student_rejected",
                payload={
                    "student_id": student.id,
                    "student_name": user.full_name,
                    "rejected_by": approver.full_name if approver else "System",
                },
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
            "student_name": creator.full_name
            if creator
            else (
                student.user.full_name if getattr(student, "user", None) else "Unknown"
            ),
            "created_by": creator.full_name if creator else "System",
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
