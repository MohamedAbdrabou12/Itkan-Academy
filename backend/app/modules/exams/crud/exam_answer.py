from typing import List, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.exams.models.exam_answer import ExamAnswer
from app.modules.exams.schemas.exam_answer import (
    ExamAnswerBulkItem,
    ExamAnswerCreate,
    ExamAnswerUpdate,
    ExamAnswerBulkCreate,
    ExamAnswerBulkItemSubmit,
)
from app.modules.users.models import User
from fastapi import HTTPException, status

from app.modules.exams.schemas.exam_attempt import ExamGradeRequest


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
        answers_in: List[ExamAnswerBulkItemSubmit],
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

    async def update_bulk(
        self,
        db: AsyncSession,
        answers_in: List[ExamGradeRequest],
        exam_answers: Sequence[ExamAnswer],
    ):
        for answer in answers_in:
            db_answer = next(
                (a for a in exam_answers if a.question_id == answer.question_id),
                None,
            )
            if not db_answer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="لم يتم ايجاد اجابة للسؤال في الامتحان",
                )
            db_answer.marks_obtained = answer.marks_obtained
        await db.commit()

    async def delete(self, db: AsyncSession, *, id: int):
        db_obj = await db.get(ExamAnswer, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj


exam_answer_crud = ExamAnswerCRUD()
