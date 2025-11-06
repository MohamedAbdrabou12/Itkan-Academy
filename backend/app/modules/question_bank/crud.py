# backend/app/modules/question_bank/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import Request

from app.modules.question_bank.models import QuestionBank
from app.modules.question_bank.schemas import QuestionBankCreate, QuestionBankUpdate


class QuestionBankCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[QuestionBank]:
        query = QuestionBank.__table__.select().order_by(QuestionBank.created_at.desc())

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                query = query.where(QuestionBank.branch_id == branch_id)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, question_id: int, request: Optional[Request] = None
    ) -> Optional[QuestionBank]:
        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = (
                    QuestionBank.__table__.select()
                    .where(QuestionBank.id == question_id)
                    .where(QuestionBank.branch_id == branch_id)
                )
                result = await db.execute(stmt)
                return result.scalars().first()

        return await db.get(QuestionBank, question_id)

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
