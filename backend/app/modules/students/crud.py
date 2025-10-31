from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreate, StudentUpdate


class StudentCRUD:
    async def get_all(self, db: AsyncSession) -> List[Student]:
        result = await db.execute(Student.__table__.select().order_by(Student.id))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, student_id: int) -> Optional[Student]:
        result = await db.get(Student, student_id)
        return result

    async def create(self, db: AsyncSession, student_in: StudentCreate) -> Student:
        student = Student(**student_in.dict())
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student

    async def update(
        self, db: AsyncSession, student: Student, student_in: StudentUpdate
    ) -> Student:
        for field, value in student_in.dict(exclude_unset=True).items():
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
