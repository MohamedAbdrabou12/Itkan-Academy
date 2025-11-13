from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.modules.exams.crud.exam import exam_crud
from app.modules.exams.crud.exam_attempt import exam_attempt_crud
from app.modules.exams.models.exam import ExamStatus

from app.modules.users.models import User
from app.modules.exams.models.exam_attempt import ExamAttemptStatus
from app.modules.exams.schemas.exam_attempt import ExamAttemptCreate


class ExamAttemptService:
    async def start_exam(self, db: AsyncSession, exam_id: int, user: User):
        exam = await exam_crud.get(db, id=exam_id, user=user)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found"
            )
        if exam.status != ExamStatus.PUBLISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam is not published yet.",
            )
        # Check if the exam has started and not ended yet

        now = datetime.now(timezone.utc)
        if not (exam.start_time <= now <= exam.end_time):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam is not currently active.",
            )

        # Check if the user has already started an attempt for this exam
        existing_attempt = await exam_attempt_crud.get_by_user_and_exam(
            db, user_id=user.id, exam_id=exam_id
        )

        if existing_attempt:
            if existing_attempt.status != ExamAttemptStatus.STARTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already submitted this exam.",
                )
            return existing_attempt  # Return existing started attempt

        exam_attempt_in = ExamAttemptCreate(exam_id=exam_id)
        return await exam_attempt_crud.create(db, obj_in=exam_attempt_in, user=user)


exam_attempt_service = ExamAttemptService()
