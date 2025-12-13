# backend/app/modules/question_bank/crud.py
from sqlalchemy import or_, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.modules.users.models import User
from app.modules.question_bank.models import QuestionBank
from app.modules.question_bank.schemas import QuestionBankCreate


class QuestionBankCRUD:
    async def get_all(self, db: AsyncSession, user: User, with_shared: bool = False):
        # get all questions with creator_id or creator_id and shared = true
        if with_shared:
            stmt = select(QuestionBank).where(
                or_(QuestionBank.created_by == user.id, QuestionBank.is_shared)
            )
            result = await db.execute(stmt)
            return result.scalars().all()
        else:
            stmt = select(QuestionBank).where(QuestionBank.created_by == user.id)
            result = await db.execute(stmt)
            return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, question_id: int, user: User, with_shared: bool = False
    ):
        if with_shared:
            stmt = select(QuestionBank).where(
                or_(
                    and_(
                        QuestionBank.id == question_id,
                        QuestionBank.created_by == user.id,
                    ),
                    and_(QuestionBank.id == question_id, QuestionBank.is_shared),
                )
            )
            result = await db.execute(stmt)
            return result.scalars().first()
        else:
            stmt = select(QuestionBank).where(
                and_(QuestionBank.id == question_id, QuestionBank.created_by == user.id)
            )
            result = await db.execute(stmt)
            return result.scalars().first()

    async def get_by_title_and_creator(
        self, db: AsyncSession, title: str, created_by: int
    ) -> Optional[QuestionBank]:
        stmt = select(QuestionBank).where(
            and_(QuestionBank.title == title, QuestionBank.created_by == created_by)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        question_in: QuestionBankCreate,
        user: User,
        active_branch_id: int,
    ):
        question_date = question_in.model_dump()
        question_date["created_by"] = user.id
        question_date["branch_id"] = active_branch_id
        question = QuestionBank(**question_date)
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    async def update(
        self, db: AsyncSession, question: QuestionBank, question_in: QuestionBankCreate
    ) -> QuestionBank:
        # update question with new values in question_in
        data = question_in.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(question, field, value)
        db.add(question)
        await db.commit()
        await db.refresh(question)
        return question

    # async def delete(self, db: AsyncSession, question_id: int) -> None:
    #     question = await self.get_by_id(db, question_id)
    #     if question:
    #         await db.delete(question)
    #         await db.commit()


question_bank_crud = QuestionBankCRUD()
