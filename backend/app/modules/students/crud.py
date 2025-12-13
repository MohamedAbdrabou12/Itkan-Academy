from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload, joinedload
from app.modules.students.models import Student, StudentClass
from app.modules.users.models import User


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
            selectinload(Student.classes), joinedload(Student.user)
        )

        if status:
            stmt = stmt.join(Student.user).where(User.status == status)

        result = await db.execute(stmt)
        students = result.scalars().all()

        if search:
            search_lower = search.lower()
            students = [
                s
                for s in students
                if search_lower in s.user.full_name.lower()
                or (s.user.email and search_lower in s.user.email.lower())
                or (s.national_id and search_lower in s.national_id.lower())
            ]

        if sort_by:
            reverse = sort_order.lower() == "desc"
            if sort_by in {"full_name", "email", "status"}:
                students.sort(key=lambda s: getattr(s.user, sort_by), reverse=reverse)
            elif sort_by in {"admission_date", "curriculum_progress", "national_id"}:
                students.sort(key=lambda s: getattr(s, sort_by), reverse=reverse)
            else:
                students.sort(key=lambda s: s.id, reverse=reverse)
        else:
            students.sort(key=lambda s: s.id)

        return students

    async def get_by_id(self, db: AsyncSession, student_id: int) -> Optional[Student]:
        stmt = (
            select(Student)
            .where(Student.id == student_id)
            .options(selectinload(Student.classes), joinedload(Student.user))
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[Student]:
        stmt = select(Student).where(Student.user_id == user_id)
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

    async def delete(self, db: AsyncSession, student: Student) -> None:
        await db.delete(student)
        await db.commit()

    async def update_student_classes(
        self, db: AsyncSession, student: Student, class_ids: List[int]
    ):
        await db.execute(
            delete(StudentClass).where(StudentClass.student_id == student.id)
        )
        for cid in class_ids:
            db.add(StudentClass(student_id=student.id, class_id=cid))
        await db.commit()


student_crud = StudentCRUD()
