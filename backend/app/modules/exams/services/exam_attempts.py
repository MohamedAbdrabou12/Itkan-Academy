from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.crud.exam_attempt import exam_attempt_crud
from app.modules.exams.models.exam import ExamStatus

from app.modules.users.models import User
from app.modules.exams.models.exam_attempt import ExamAttemptStatus
from app.modules.exams.schemas.exam_attempt import ExamAttemptCreate
from app.modules.exams.crud.exam_answer import exam_answer_crud


class ExamAttemptService:
    async def start_exam(self, db: AsyncSession, exam_id: int, user: User):
        exam = await exam_crud.get_exam_by_id(db, id=exam_id)
        user_branches = user.branches
        user_class_ids = []
        for branch in user_branches:
            for classObj in branch.classes:
                user_class_ids.append(classObj.id)

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="الامتحان غير موجود"
            )

        if exam.class_id not in user_class_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="غير مصرح لك باجراء هذا الامتحان",
            )

        if exam.status != ExamStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="لا يمكنك اجراء الامتحان الان",
            )
        # Check if the exam has started and not ended yet

        now = datetime.now(timezone.utc)
        if not (exam.start_time <= now <= exam.end_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="الامتحان غير متاح الان",
            )

        # Check if the user has already started an attempt for this exam
        existing_attempt = await exam_attempt_crud.get_by_user_and_exam(
            db, user_id=user.id, exam_id=exam_id
        )

        if existing_attempt:
            if existing_attempt.status != ExamAttemptStatus.STARTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="لقد قمت بتسليم الامتحان من قبل",
                )
            return existing_attempt  # Return existing started attempt

        exam_attempt_in = ExamAttemptCreate(exam_id=exam_id)
        return await exam_attempt_crud.create(db, obj_in=exam_attempt_in, user=user)

    async def get_exam_attempts(self, db: AsyncSession, exam_id: int, user: User):
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="الامتحان غير موجود"
            )

        attempts = await exam_attempt_crud.get_exam_attempts(db, exam_id=exam_id)
        return attempts

    async def get_exam_attempt(self, db: AsyncSession, attempt_id: int, user: User):
        return await exam_attempt_crud.get(db, attempt_id)

    async def grade_exam(self, db: AsyncSession, id: int, exam_answers: list):
        db_exam_answers = await exam_answer_crud.get_multi_by_attempt(db, attempt_id=id)
        if not db_exam_answers:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="لم يتم ايجاد الاجابات القديمة للامتحان",
            )

        await exam_answer_crud.update_bulk(db, exam_answers, db_exam_answers)

        return await exam_attempt_crud.grade_exam(db, id=id, exam_answers=exam_answers)


exam_attempt_service = ExamAttemptService()
