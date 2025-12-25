from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_
from sqlalchemy.orm import selectinload, joinedload
from app.modules.students.models import Student, StudentClass
from app.modules.users.models import User, UserBranch


class StudentCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
    ) -> List[Student]:
        stmt = select(Student).options(
            selectinload(Student.classes),
            joinedload(Student.user).selectinload(User.role),
            joinedload(Student.user)
            .selectinload(User.branch_links)
            .joinedload(UserBranch.branch),
        )

        if status or search:
            stmt = stmt.join(Student.user)

        if status:
            stmt = stmt.where(User.status == status)

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    Student.national_id.ilike(search_term),
                )
            )

        result = await db.execute(stmt)
        students = list(result.scalars().all())

        if sort_by:
            reverse = sort_order.lower() == "desc"
            if sort_by in {"full_name", "email", "status"}:
                students.sort(
                    key=lambda s: getattr(s.user, sort_by) or "", reverse=reverse
                )
            elif sort_by in {"admission_date", "national_id"}:
                students.sort(key=lambda s: getattr(s, sort_by) or "", reverse=reverse)
            else:
                students.sort(key=lambda s: s.id, reverse=reverse)
        else:
            students.sort(key=lambda s: s.id)

        return students

    async def get_by_id(self, db: AsyncSession, student_id: int) -> Optional[Student]:
        stmt = (
            select(Student)
            .where(Student.id == student_id)
            .options(
                selectinload(Student.classes),
                joinedload(Student.user).selectinload(User.role),
                joinedload(Student.user)
                .selectinload(User.branch_links)
                .joinedload(UserBranch.branch),
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_class_ids(
        self, db: AsyncSession, class_ids: List[int]
    ) -> List[Student]:
        stmt = (
            select(Student)
            .options(joinedload(Student.user))
            .join(StudentClass)
            .where(StudentClass.class_id.in_(class_ids))
            .distinct(Student.id)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Student]:
        stmt = (
            select(Student)
            .where(Student.user_id == user_id)
            .options(joinedload(Student.user))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, student_payload: dict) -> Student:
        student = Student(**student_payload)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def update(self, db: AsyncSession, student: Student, data: dict) -> Student:
        for field, value in data.items():
            setattr(student, field, value)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def update_student_classes(
        self, db: AsyncSession, student: Student, class_ids: List[int]
    ):
        await db.execute(
            delete(StudentClass).where(StudentClass.student_id == student.id)
        )

        if class_ids:
            new_classes = [
                StudentClass(student_id=student.id, class_id=cid) for cid in class_ids
            ]
            db.add_all(new_classes)

        await db.commit()
        await db.refresh(student)


student_crud = StudentCRUD()
