from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.modules.exams.models.exam_answer import ExamAnswer
from app.modules.exams.schemas.exam_answer import ExamAnswerCreate, ExamAnswerUpdate


class ExamAnswerCRUD:
    async def get_all(
        self, db: AsyncSession, attempt_id: Optional[int] = None
    ) -> List[ExamAnswer]:
        query = select(ExamAnswer)
        if attempt_id:
            query = query.where(ExamAnswer.attempt_id == attempt_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, answer_id: int) -> Optional[ExamAnswer]:
        result = await db.execute(select(ExamAnswer).where(ExamAnswer.id == answer_id))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: ExamAnswerCreate) -> ExamAnswer:
        exam_answer = ExamAnswer(**obj_in.dict())
        db.add(exam_answer)
        await db.commit()
        await db.refresh(exam_answer)
        return exam_answer

    async def update(
        self,
        db: AsyncSession,
        exam_answer: ExamAnswer,
        obj_in: ExamAnswerUpdate,
    ) -> ExamAnswer:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(exam_answer, field, value)
        db.add(exam_answer)
        await db.commit()
        await db.refresh(exam_answer)
        return exam_answer

    async def delete(self, db: AsyncSession, answer_id: int) -> None:
        exam_answer = await self.get_by_id(db, answer_id)
        if exam_answer:
            await db.delete(exam_answer)
            await db.commit()


exam_answer_crud = ExamAnswerCRUD()
