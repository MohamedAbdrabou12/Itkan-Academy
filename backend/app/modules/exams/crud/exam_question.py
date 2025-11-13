from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.modules.exams.models.exam_question import ExamQuestion
from app.modules.exams.schemas.exam_question import (
    ExamQuestionCreate,
    ExamQuestionUpdate,
)
from app.modules.users.models import User


class ExamQuestionCRUD:
    async def get(self, db: AsyncSession, id: int) -> Optional[ExamQuestion]:
        result = await db.execute(select(ExamQuestion).filter(ExamQuestion.id == id))
        return result.scalars().first()

    async def get_multi_by_exam(
        self, db: AsyncSession, *, exam_id: int, skip: int = 0, limit: int = 100
    ):
        result = await db.execute(
            select(ExamQuestion)
            .filter(ExamQuestion.exam_id == exam_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, *, obj_in: ExamQuestionCreate, exam_id: int, user: User
    ) -> ExamQuestion:
        db_obj = ExamQuestion(
            **obj_in.model_dump(),
            exam_id=exam_id,
            branch_id=user.branch_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_mult_questions(
        self,
        db: AsyncSession,
        obj_in: List[ExamQuestionCreate],
        exam_id: int,
        user: User,
    ) -> List[ExamQuestion]:
        db_objs = []
        for item in obj_in:
            data = item.model_dump(exclude_unset=True, exclude_none=True)
            db_obj = ExamQuestion(
                **data,
                exam_id=exam_id,
                branch_id=user.branch_id,
            )
            db.add(db_obj)
            db_objs.append(db_obj)

        await db.commit()
        for db_obj in db_objs:
            await db.refresh(db_obj)

        return db_objs

    async def update(
        self, db: AsyncSession, *, db_obj: ExamQuestion, obj_in: ExamQuestionUpdate
    ) -> ExamQuestion:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int) -> Optional[ExamQuestion]:
        result = await db.execute(select(ExamQuestion).filter(ExamQuestion.id == id))
        db_obj = result.scalars().first()
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


exam_question_crud = ExamQuestionCRUD()
