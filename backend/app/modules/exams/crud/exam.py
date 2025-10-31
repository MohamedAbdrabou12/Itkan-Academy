from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime

from app.modules.exams.models.exam import Exam
from app.modules.exams.schemas.exam import ExamCreate, ExamUpdate


class ExamCRUD:
    async def get_all(self, db: AsyncSession) -> List[Exam]:
        result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, exam_id: int) -> Optional[Exam]:
        return await db.get(Exam, exam_id)

    async def create(self, db: AsyncSession, exam_in: ExamCreate) -> Exam:
        exam = Exam(**exam_in.dict())
        db.add(exam)
        await db.commit()
        await db.refresh(exam)
        return exam

    async def update(self, db: AsyncSession, exam: Exam, exam_in: ExamUpdate) -> Exam:
        for field, value in exam_in.dict(exclude_unset=True).items():
            setattr(exam, field, value)
        exam.updated_at = datetime.utcnow()
        db.add(exam)
        await db.commit()
        await db.refresh(exam)
        return exam

    async def delete(self, db: AsyncSession, exam_id: int) -> None:
        exam = await self.get_by_id(db, exam_id)
        if exam:
            await db.delete(exam)
            await db.commit()


exam_crud = ExamCRUD()
