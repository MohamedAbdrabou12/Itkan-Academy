from typing import List, Optional

from app.modules.evaluations.models import Evaluation
from app.modules.evaluations.schemas import EvaluationCreate, EvaluationUpdate
from sqlalchemy.ext.asyncio import AsyncSession


class DailyEvaluationCRUD:
    async def get_all(self, db: AsyncSession) -> List[Evaluation]:
        result = await db.execute(
            Evaluation.__table__.select().order_by(Evaluation.date)
        )
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, eval_id: int
    ) -> Optional[Evaluation]:
        result = await db.get(Evaluation, eval_id)
        return result

    async def create(
        self, db: AsyncSession, eval_in: EvaluationCreate
    ) -> Evaluation:
        evaluation = Evaluation(**eval_in.dict())
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)
        return evaluation

    async def update(
        self,
        db: AsyncSession,
        evaluation: Evaluation,
        eval_in: EvaluationUpdate,
    ) -> Evaluation:
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
