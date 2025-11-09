# backend/app/modules/students/service.py
from datetime import datetime
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
        return {
            "id": student.id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "role_id": user.role_id if user else None,
            "branch_id": user.branch_id if user else None,
            "status": user.status if user else None,
            "parent_name": student.parent_name,
            "class_id": student.class_id,
            "admission_date": student.admission_date,
            "curriculum_progress": student.curriculum_progress,
            "created_at": student.created_at,
            "updated_at": student.updated_at,
        }

    @staticmethod
    async def list_students(db: AsyncSession, status: Optional[str] = None) -> List[Dict]:
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
        # Email must be unique
        existing = await user_crud.get_by_email(db, student_in.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Branch validation
        if creator and getattr(creator, "role_name", "").lower() != "admin":
            if student_in.branch_id is None or student_in.branch_id != creator.branch_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="branch_id must match creator's branch",
                )

        # Class belongs to same branch if class_id provided
        if student_in.class_id:
            cls = await db.get(Class, student_in.class_id)
            if not cls:
                raise HTTPException(status_code=404, detail="Class not found")
            if cls.branch_id != student_in.branch_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="class_id does not belong to the provided branch",
                )

        #  Always use role student from DB
        student_role = await db.execute(select(Role).where(Role.name.ilike("student")))
        student_role = student_role.scalar_one_or_none()
        role_id = student_role.id if student_role else student_in.role_id

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
            "class_id": student_in.class_id,
            "admission_date": student_in.admission_date,
            "curriculum_progress": student_in.curriculum_progress,
        }
        student = await student_crud.create(db, student_payload)

        await StudentService._notify_hr_new_student(db, student, creator)

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def update_student(db: AsyncSession, student_id: int, student_in: StudentUpdate) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # load user
        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        data = student_in.dict(exclude_unset=True)

        # Update user-shared fields
        user_fields = {}
        for f in ("name", "email", "phone", "branch_id"):
            if f in data:
                user_fields[f] = data.pop(f)
        if user_fields:
            # email uniqueness check if email is changed
            if "email" in user_fields and user_fields["email"] != user.email:
                exist = await user_crud.get_by_email(db, user_fields["email"])
                if exist:
                    raise HTTPException(status_code=400, detail="Email already registered")
            # this will handle updating user fields and commit
            updated_user = await user_crud.update(db, user, UserUpdate(**user_fields))

        # Update student-only fields
        student_fields = data
        if student_fields:
            student = await student_crud.update(db, student, student_fields)

        # refresh and serialize
        student.user = await db.get(User, student.user_id)
        return await StudentService._serialize_student(student)

    # student deletion is soft-deactivation of linked user  
    @staticmethod
    async def delete_student(db: AsyncSession, student_id: int) -> dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        # prevent delete if attendance or invoices exist
        attendance_exists = bool(student.attendance_records)
        payment_exists = bool(student.invoices)
        if attendance_exists or payment_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete student with attendance or payments",
            )

        # soft deactivate user and do not delete student
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
    async def approve_student(db: AsyncSession, student_id: int, approver: Optional[User] = None) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")

        # Approver must have permission checked at route level here just set status
        user.status = UserStatus.active.value
        db.add(user)
        await db.commit()
        await db.refresh(student)

        # notify student (web) that approved (optional)
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
        except Exception:           #later we can change it to log the error depending on our logging strategy
            pass

        student.user = user
        return await StudentService._serialize_student(student)

    @staticmethod
    async def reject_student(db: AsyncSession, student_id: int, approver: Optional[User] = None) -> Dict:
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
    async def _notify_hr_new_student(db: AsyncSession, student: Student, creator: Optional[User] = None):
        from app.modules.roles.models import Role
        from app.modules.users.models import User as UserModel
        # check for HR or admin users to notify
        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        hr_role = role_res.scalar_one_or_none()    # later we can add hr role also to get notified
        if not hr_role:
            return

        res = await db.execute(select(UserModel).where(UserModel.role_id == hr_role.id))
        hr_users = res.scalars().all()
        if not hr_users:
            return

        payload = {
            "student_id": student.id,
            "student_name": creator.name if creator else (student.user.name if getattr(student, "user", None) else "Unknown"),
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