from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.modules.users.models import User
from app.modules.exams.schemas.exam import ExamQuestionWithDetails, ExamRead
from app.modules.exams.schemas.exam_question import (
    ExamQuestionCreate,
    ExamQuestionUpdate,
)
from app.modules.exams.services import exam_question_service

exam_question_router = APIRouter(tags=["Exam Questions"])


@exam_question_router.post(
    "/exams/{exam_id}/questions",
    status_code=status.HTTP_201_CREATED,
    response_model=ExamRead,
)
async def add_questions_to_exam(
    exam_id: int,
    question_in: list[ExamQuestionCreate],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_question_service.add_questions_to_exam(
        db, exam_id=exam_id, questions_in=question_in, user=user
    )


@exam_question_router.get(
    "/exams/{exam_id}/questions", response_model=List[ExamQuestionWithDetails]
)
async def get_exam_questions(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_question_service.get_questions_for_exam(
        db, exam_id=exam_id, user=user
    )


@exam_question_router.put(
    "/exams/{exam_id}/questions/{question_id}", response_model=ExamRead
)
async def update_exam_question(
    exam_id: int,
    question_id: int,
    question_in: ExamQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_question_service.update_question_in_exam(
        db,
        exam_id=exam_id,
        question_id=question_id,
        question_in=question_in,
        user=user,
    )


@exam_question_router.delete(
    "/exams/{exam_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exam_question(
    exam_id: int,
    question_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await exam_question_service.remove_question_from_exam(
        db, exam_id=exam_id, question_id=question_id, user=user
    )
    return
