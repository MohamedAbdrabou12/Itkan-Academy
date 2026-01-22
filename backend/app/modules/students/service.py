from typing import Dict, List, Optional

from app.core.utils import create_password_reset_token
from app.modules.classes.models import Class
from app.modules.roles.models import Role
from app.modules.students.crud import student_crud
from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreate, StudentUpdate
from app.modules.users.crud import user_crud
from app.modules.users.models import User, UserBranch, UserStatus
from app.modules.users.schemas import (
    BranchInfo,
    UserCreate,
)
from app.services.notification_service.workrs.worker import send_notification_task
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.modules.parents.models import Parent, ParentStudent


class StudentService:
    @staticmethod
    async def _serialize_student(student: Student) -> Dict:
        user: User = student.user
        if not user:
            return {}

        role_name = user.role.name if user.role else None
        role_name_ar = getattr(user.role, "name_ar", None) if user.role else None

        branch_ids = []
        branches_info = []
        primary_branch_name = None

        if user.branch_links:
            for link in user.branch_links:
                branch_ids.append(link.branch_id)
                if link.branch:
                    branches_info.append(BranchInfo.from_orm(link.branch))
                    if not primary_branch_name:
                        primary_branch_name = link.branch.name

        user_data = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "role_id": user.role_id,
            "role_name": role_name,
            "role_name_ar": role_name_ar,
            "login_identifier": user.login_identifier,
            "login_type": user.login_type,
            "branch_name": primary_branch_name,
            "status": user.status,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "branch_ids": branch_ids,
            "branches": branches_info,
        }

        class_ids = [c.id for c in getattr(student, "classes", [])]

        return {
            **user_data,
            "student_id": student.id,
            "national_id": student.national_id,
            "class_ids": class_ids,
            "admission_date": student.admission_date,
            "curriculum_progress": student.curriculum_progress,
        }

    @staticmethod
    async def list_students(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        status: Optional[str] = None,
    ) -> Dict:
        students = await student_crud.get_all(
            db, status=status, search=search, sort_by=sort_by, sort_order=sort_order
        )

        total = len(students)
        start = (page - 1) * size
        end = start + size
        page_items = students[start:end]

        serialized = []
        for s in page_items:
            serialized.append(await StudentService._serialize_student(s))

        return {
            "items": serialized,
            "page": page,
            "size": size,
            "total": total,
            "pages": (total + size - 1) // size,
        }

    @staticmethod
    async def get_student(db: AsyncSession, student_id: int) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return await StudentService._serialize_student(student)

    @staticmethod
    async def create_student(
        db: AsyncSession, student_in: StudentCreate, creator: Optional[User] = None
    ) -> Dict:
        if await user_crud.get_by_login_identifier(db, student_in.national_id):
            raise HTTPException(
                status_code=400, detail="National ID already registered"
            )

        if student_in.email and await user_crud.get_by_email(db, student_in.email):
            raise HTTPException(status_code=400, detail="Email already registered")

        if creator and getattr(creator, "role_name", "") != "General Manager":
            creator_branches = [
                link.branch_id for link in getattr(creator, "branch_links", [])
            ]

            if not any(b in creator_branches for b in (student_in.branch_ids or [])):
                raise HTTPException(
                    status_code=400,
                    detail="Student branches must match creator's branches",
                )
                
#         Validate creator branch permissions
#         if creator and getattr(creator, "role_name", "").lower() != "admin":
#             creator_branches = getattr(creator, "branch_ids", [])
#             student_branches = student_in.branch_ids or []

#             if creator_branches:
#                 if not any(b in creator_branches for b in student_branches):
#                     raise HTTPException(
#                         status_code=400,
#                         detail="Student branches must match creator's branches",
#                     )
                    
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
                        status_code=400,
                        detail=f"Class {cid} does not belong to provided branches",
                    )
                class_objs.append(cls)

        role_res = await db.execute(select(Role).where(Role.name.ilike("student")))
        student_role = role_res.scalar_one_or_none()

        user_payload = UserCreate(
            full_name=student_in.full_name,
            email=student_in.email,
            phone=student_in.phone,
            role_id=student_role.id if student_role else None,
            branch_ids=student_in.branch_ids,
            status=student_in.status or UserStatus.pending,
            password=student_in.password,
            login_identifier=student_in.national_id,
            login_type="national_id",
        )

        if not student_in.password:
            raise HTTPException(status_code=400, detail="Password is required")

        user = await user_crud.create(db, user_payload)

        student_payload = {
            "user_id": user.id,
            "national_id": student_in.national_id,
            "admission_date": student_in.admission_date,
            "curriculum_progress": student_in.curriculum_progress,
        }
        student = await student_crud.create(db, student_payload)

        if class_objs:
            student.classes = class_objs
            await db.commit()

        from app.modules.parents.models import ParentStudent, Parent

        user_res = await db.execute(
            select(User)
            .options(
                selectinload(User.student)
                .selectinload(Student.parent_links)
                .selectinload(ParentStudent.parent)
                .selectinload(Parent.user)
            )
            .where(User.id == user.id)
        )
        user_full = user_res.scalar_one()
        await StudentService._send_reset_password_notification(db, user_full)

        full_student = await student_crud.get_by_id(db, student.id)
        await StudentService._notify_hr_new_student(db, full_student, creator)

        return await StudentService._serialize_student(full_student)

    @staticmethod
    async def update_student(
        db: AsyncSession, student_id: int, student_in: StudentUpdate
    ) -> Dict:
        # Load student with relationships to avoid session issues
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        data = student_in.dict(exclude_unset=True)

        if "national_id" in data:
            new_nid = data["national_id"]
            if new_nid != student.national_id:
                existing = await student_crud.get_all(db, search=new_nid)
                if any(
                    s.id != student.id and s.national_id == new_nid for s in existing
                ):
                    raise HTTPException(
                        status_code=400, detail="National ID already registered"
                    )
                user = await db.get(User, student.user_id)
                user.login_identifier = new_nid

        user_fields = [
            "full_name",
            "email",
            "phone",
            "branch_ids",
            "status",
            "password",
        ]
        user_update_data = {f: data.pop(f) for f in user_fields if f in data}

        if user_update_data:
            user = await db.get(User, student.user_id)
            await user_crud.update(db, user, UserUpdate(**user_update_data))

        if "class_ids" in data:
            class_ids = data.pop("class_ids")
            await student_crud.update_student_classes(db, student, class_ids)
            student = await student_crud.get_by_id(db, student_id)

        if data:
            await student_crud.update(db, student, data)

        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def delete_student(db: AsyncSession, student_id: int) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if getattr(student, "attendance_records", []) or getattr(
            student, "invoices", []
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot delete student with attendance or payments",
            )
        student = result.scalars().unique().one()

        user = await db.get(User, student.user_id)
        user.status = UserStatus.deactive.value
        await db.commit()

        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def approve_student(
        db: AsyncSession, student_id: int, approver: Optional[User] = None
    ) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        user.status = UserStatus.active.value
        await db.commit()

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

        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def reject_student(
        db: AsyncSession, student_id: int, approver: Optional[User] = None
    ) -> Dict:
        student = await student_crud.get_by_id(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        user = await db.get(User, student.user_id)
        user.status = UserStatus.rejected.value
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

        return await StudentService.get_student(db, student_id)

    @staticmethod
    async def _send_reset_password_notification(db: AsyncSession, user: User):
        recipients = []
        if user.email:
            recipients.append(user.email)

        if not recipients and user.student:
            for link in getattr(user.student, "parent_links", []):
                parent_user = getattr(link.parent, "user", None)
                if parent_user and parent_user.email:
                    recipients.append(parent_user.email)

        if not recipients:
            return

        token = create_password_reset_token(user.id)
        reset_link = f"http://localhost:5173/reset-password?token={token}"

        for email in list(set(recipients)):
            send_notification_task.delay(
                user_id=str(user.id),
                channel="email",
                template_type="password_reset_request",
                payload={
                    "user_name": user.full_name,
                    "email": email,
                    "reset_link": reset_link,
                },
            )

    @staticmethod
    async def _notify_hr_new_student(
        db: AsyncSession, student: Student, creator: Optional[User] = None
    ):
        role_res = await db.execute(select(Role).where(Role.name.ilike("admin")))
        hr_role = role_res.scalar_one_or_none()
        if not hr_role:
            return

        res = await db.execute(select(User).where(User.role_id == hr_role.id))
        hr_users = res.scalars().all()

        payload = {
            "student_id": student.id,
            "student_name": student.user.full_name if student.user else "Unknown",
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

    @staticmethod
    async def get_students_by_classes(
        db: AsyncSession, class_ids: List[int]
    ) -> List[Dict]:
        students = await student_crud.get_by_class_ids(db, class_ids)
        return [{"id": s.id, "name": s.user.full_name} for s in students]
