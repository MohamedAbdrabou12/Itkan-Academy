from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.question_bank.models import QuestionBank
from app.modules.question_bank.schemas import QuestionBankCreate, QuestionBankUpdate


class QuestionBankCRUD:
    async def get_all(self, db: AsyncSession) -> List[QuestionBank]:
        result = await db.execute(
            QuestionBank.__table__.select().order_by(QuestionBank.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, question_id: int
    ) -> Optional[QuestionBank]:
        result = await db.get(QuestionBank, question_id)
        return result

    async def create(
        self, db: AsyncSession, question_in: QuestionBankCreate
    ) -> QuestionBank:
        question = QuestionBank(**question_in.dict())
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    async def update(
        self, db: AsyncSession, question: QuestionBank, question_in: QuestionBankUpdate
    ) -> QuestionBank:
        for field, value in question_in.dict(exclude_unset=True).items():
            setattr(question, field, value)
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    async def delete(self, db: AsyncSession, question_id: int) -> None:
        question = await self.get_by_id(db, question_id)
        if question:
            await db.delete(question)
            await db.commit()


question_bank_crud = QuestionBankCRUD()
