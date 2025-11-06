# backend/app/modules/students/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Request

from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreate, StudentUpdate


class StudentCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[Student]:
        stmt = select(Student).order_by(Student.id)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(Student.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, student_id: int, request: Optional[Request] = None
    ) -> Optional[Student]:
        stmt = select(Student).where(Student.id == student_id)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = stmt.where(Student.branch_id == branch_id)

        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, student_in: StudentCreate) -> Student:
        student = Student(**student_in.dict())
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def update(
        self, db: AsyncSession, student: Student, student_in: StudentUpdate
    ) -> Student:
        data = student_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(student, field, value)
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def delete(self, db: AsyncSession, student_id: int) -> None:
        student = await self.get_by_id(db, student_id)
        if student:
            await db.delete(student)
            await db.commit()


student_crud = StudentCRUD()
