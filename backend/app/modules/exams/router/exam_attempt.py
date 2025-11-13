from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.users.models import User
from app.modules.exams.crud.exam_attempt import exam_attempt_crud
from app.modules.exams.services import exam_attempt_service
from app.modules.exams.schemas.exam_attempt import (
    ExamAttemptRead,
    ExamAttemptCreate,
    ExamAttemptResponse,
    ExamQuestionAnswers,
)

exam_attempts_router = APIRouter(prefix="/exam-attempts", tags=["Exam Attempts"])


@exam_attempts_router.get(
    "/",
    response_model=List[ExamAttemptRead],
)
async def list_attempts(
    db: AsyncSession = Depends(get_db),
):
    # Further filtering by exam, student, class would be implemented here
    return await exam_attempt_crud.get_multi(db)


# for teacher
@exam_attempts_router.get(
    "/{id}",
    response_model=ExamAttemptResponse,
)
async def get_attempt(id: int, db: AsyncSession = Depends(get_db)):
    return await exam_attempt_crud.get(db, id)


@exam_attempts_router.post(
    "/start",
    response_model=ExamAttemptRead,
    status_code=status.HTTP_201_CREATED,
)
async def start_exam(
    exam_attempt_in: ExamAttemptCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_attempt_service.start_exam(
        db, exam_id=exam_attempt_in.exam_id, user=user
    )


# for teachers
@exam_attempts_router.post(
    "/{id}/grade",
    response_model=ExamAttemptRead,
)
async def grade_exam(
    id: int,
    exam_answers: list[ExamQuestionAnswers],
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await exam_attempt_crud.grade_exam(db, id=id, exam_answers=exam_answers)
