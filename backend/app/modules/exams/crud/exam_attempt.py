from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.modules.exams.models.exam_attempt import ExamAttempt, ExamAttemptStatus
from app.modules.exams.schemas.exam_attempt import (
    ExamAttemptCreate,
    ExamAttemptUpdate,
    ExamQuestionAnswers,
    ExamGradeRequest,
)
from app.modules.users.models import User
from sqlalchemy.orm import selectinload

from app.modules.exams.models.exam_answer import ExamAnswer
from app.modules.exams.models.exam import Exam
from app.modules.exams.models.exam_question import ExamQuestion


class ExamAttemptCRUD:
    async def create(
        self, db: AsyncSession, *, obj_in: ExamAttemptCreate, user: User
    ) -> ExamAttempt:
        examAttempt = obj_in.model_dump()
        examAttempt["student_id"] = user.id
        examAttempt["status"] = ExamAttemptStatus.STARTED
        db_obj = ExamAttempt(**examAttempt)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> Optional[ExamAttempt]:
        result = await db.execute(
            select(ExamAttempt)
            .options(
                selectinload(ExamAttempt.exam).options(selectinload(Exam.questions))
            )
            .options(
                selectinload(ExamAttempt.answers).options(
                    selectinload(ExamAnswer.question)
                )
            )
            .options(
                selectinload(ExamAttempt.answers).options(
                    selectinload(ExamAnswer.question).options(
                        selectinload(ExamQuestion.question)
                    )
                )
            )
            .options(
                selectinload(ExamAttempt.student), selectinload(ExamAttempt.student)
            )
            .where(ExamAttempt.id == id)
        )
        return result.scalars().first()

    async def get_with_user(
        self, db: AsyncSession, id: int, user: User
    ) -> Optional[ExamAttempt]:
        result = await db.execute(
            select(ExamAttempt).filter(
                ExamAttempt.id == id, ExamAttempt.student_id == user.id
            )
        )
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100):
        statement = select(ExamAttempt).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_by_user_and_exam(
        self, db: AsyncSession, *, user_id: int, exam_id: int
    ) -> Optional[ExamAttempt]:
        statement = select(ExamAttempt).where(
            ExamAttempt.student_id == user_id, ExamAttempt.exam_id == exam_id
        )
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_exam_attempts(self, db: AsyncSession, *, exam_id: int):
        statement = (
            select(ExamAttempt)
            .options(selectinload(ExamAttempt.student))
            .where(ExamAttempt.exam_id == exam_id)
        )
        result = await db.execute(statement)
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, *, db_obj: ExamAttempt, obj_in: ExamAttemptUpdate
    ) -> ExamAttempt:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: int):
        db_obj = await db.get(ExamAttempt, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj

    async def grade_exam(
        self, db: AsyncSession, *, id: int, exam_answers: list[ExamGradeRequest]
    ):
        total_score = 0
        for question in exam_answers:
            total_score += question.marks_obtained

        db_obj = await db.get(ExamAttempt, id)
        if db_obj:
            db_obj.status = ExamAttemptStatus.GRADED
            db_obj.score = total_score
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj


exam_attempt_crud = ExamAttemptCRUD()
