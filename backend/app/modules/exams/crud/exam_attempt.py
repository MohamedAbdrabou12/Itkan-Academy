from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.modules.exams.models.exam_attempt import ExamAttempt
from app.modules.exams.schemas.exam_attempt import ExamAttemptCreate, ExamAttemptUpdate


class ExamAttemptCRUD:
    async def get_all(
        self, db: AsyncSession, exam_id: Optional[int] = None
    ) -> List[ExamAttempt]:
        query = select(ExamAttempt)
        if exam_id:
            query = query.where(ExamAttempt.exam_id == exam_id)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, attempt_id: int
    ) -> Optional[ExamAttempt]:
        result = await db.execute(
            select(ExamAttempt).where(ExamAttempt.id == attempt_id)
        )
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, obj_in: ExamAttemptCreate) -> ExamAttempt:
        attempt = ExamAttempt(**obj_in.dict())
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    async def update(
        self,
        db: AsyncSession,
        attempt: ExamAttempt,
        obj_in: ExamAttemptUpdate,
    ) -> ExamAttempt:
        for field, value in obj_in.dict(exclude_unset=True).items():
            setattr(attempt, field, value)
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)
        return attempt

    async def delete(self, db: AsyncSession, attempt_id: int) -> None:
        attempt = await self.get_by_id(db, attempt_id)
        if attempt:
            await db.delete(attempt)
            await db.commit()


exam_attempt_crud = ExamAttemptCRUD()
