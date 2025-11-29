# backend/app/modules/students/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload
from app.modules.students.models import Student, StudentClass
from app.modules.users.models import User


class StudentCRUD:
    async def get_all(
        self, db: AsyncSession, status: Optional[str] = None
    ) -> List[Student]:
        stmt = (
            select(Student)
            .options(selectinload(Student.classes), joinedload(Student.user))
            .order_by(Student.id)
        )
        if status:
            stmt = stmt.join(Student.user).where(User.status == status)
        result = await db.execute(stmt)
        return result.scalars().all()

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
        await db.execute(f"DELETE FROM student_classes WHERE student_id = {student.id}")
        for cid in class_ids:
            db.add(StudentClass(student_id=student.id, class_id=cid))
        await db.commit()


student_crud = StudentCRUD()
