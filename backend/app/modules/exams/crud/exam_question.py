from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.modules.exams.models.exam_question import ExamQuestion
from app.modules.exams.schemas.exam_question import (
    ExamQuestionCreate,
    ExamQuestionUpdate,
)


class ExamQuestionCRUD:
    async def get_all(
        self, db: AsyncSession, exam_id: Optional[int] = None
    ) -> List[ExamQuestion]:
        query = select(ExamQuestion)
        if exam_id:
            query = query.where(ExamQuestion.exam_id == exam_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_ids(
        self, db: AsyncSession, exam_id: int, question_id: int
    ) -> Optional[ExamQuestion]:
        result = await db.execute(
            select(ExamQuestion).where(
                ExamQuestion.exam_id == exam_id,
                ExamQuestion.question_id == question_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self, db: AsyncSession, obj_in: ExamQuestionCreate
    ) -> ExamQuestion:
        exam_question = ExamQuestion(**obj_in.dict())
        db.add(exam_question)
        await db.commit()
        await db.refresh(exam_question)
        return exam_question

    async def update(
        self,
        db: AsyncSession,
        exam_question: ExamQuestion,
        obj_in: ExamQuestionUpdate,
    ) -> ExamQuestion:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(exam_question, field, value)
        db.add(exam_question)
        await db.commit()
        await db.refresh(exam_question)
        return exam_question

    async def delete(self, db: AsyncSession, exam_id: int, question_id: int) -> None:
        exam_question = await self.get_by_ids(db, exam_id, question_id)
        if exam_question:
            await db.delete(exam_question)
            await db.commit()


exam_question_crud = ExamQuestionCRUD()
