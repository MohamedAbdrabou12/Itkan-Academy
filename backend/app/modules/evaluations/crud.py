from typing import List, Optional

from app.modules.evaluations.models import DailyEvaluation
from app.modules.evaluations.schemas import DailyEvaluationCreate, DailyEvaluationUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class DailyEvaluationCRUD:
    async def get_all(self, db: AsyncSession) -> List[DailyEvaluation]:
        result = await db.execute(
            DailyEvaluation.__table__.select().order_by(DailyEvaluation.date)
        )
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, eval_id: int
    ) -> Optional[DailyEvaluation]:
        result = await db.get(DailyEvaluation, eval_id)
        return result

    async def create(
        self, db: AsyncSession, eval_in: DailyEvaluationCreate
    ) -> DailyEvaluation:
        evaluation = DailyEvaluation(**eval_in.dict())
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def update(
        self,
        db: AsyncSession,
        evaluation: DailyEvaluation,
        eval_in: DailyEvaluationUpdate,
    ) -> DailyEvaluation:
        for field, value in eval_in.dict(exclude_unset=True).items():
            setattr(evaluation, field, value)
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def delete(self, db: AsyncSession, eval_id: int) -> None:
        evaluation = await self.get_by_id(db, eval_id)
        if evaluation:
            await db.delete(evaluation)
            await db.commit()


daily_evaluation_crud = DailyEvaluationCRUD()
