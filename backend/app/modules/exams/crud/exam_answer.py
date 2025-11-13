from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.exams.models.exam_answer import ExamAnswer
from app.modules.exams.schemas.exam_answer import (
    ExamAnswerBulkItem,
    ExamAnswerCreate,
    ExamAnswerUpdate,
    ExamAnswerBulkCreate,
)
from app.modules.users.models import User


class ExamAnswerCRUD:
    async def create(self, db: AsyncSession, *, obj_in: ExamAnswerCreate) -> ExamAnswer:
        db_obj = ExamAnswer(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def create_bulk(
        self,
        db: AsyncSession,
        *,
        attempt_id: int,
        answers_in: List[ExamAnswerBulkItem],
    ) -> List[ExamAnswer]:
        db_objs = []
        for item in answers_in:
            data = item.model_dump(exclude_unset=True, exclude_none=True)
            db_obj = ExamAnswer(
                **data,
                attempt_id=attempt_id,
            )
            db.add(db_obj)
            db_objs.append(db_obj)

        await db.commit()
        for db_obj in db_objs:
            await db.refresh(db_obj)
        return db_objs

    async def get(self, db: AsyncSession, id: int) -> Optional[ExamAnswer]:
        return await db.get(ExamAnswer, id)

    async def get_multi_by_attempt(self, db: AsyncSession, *, attempt_id: int):
        statement = select(ExamAnswer).where(ExamAnswer.attempt_id == attempt_id)
        result = await db.execute(statement)
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, *, db_obj: ExamAnswer, obj_in: ExamAnswerUpdate
    ) -> ExamAnswer:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int):
        db_obj = await db.get(ExamAnswer, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


exam_answer_crud = ExamAnswerCRUD()
