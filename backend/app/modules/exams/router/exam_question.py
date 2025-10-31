from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.exams.schemas.exam_question import (
    ExamQuestionCreate,
    ExamQuestionRead,
    ExamQuestionUpdate,
)
from app.modules.exams.crud.exam_question import exam_question_crud

router = APIRouter(prefix="/exam-questions", tags=["Exam Questions"])


@router.get(
    "/",
    response_model=List[ExamQuestionRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def list_exam_questions(db: AsyncSession = Depends(get_db)):
    return await exam_question_crud.get_all(db)


@router.get(
    "/{exam_id}/{question_id}",
    response_model=ExamQuestionRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def get_exam_question(
    exam_id: int, question_id: int, db: AsyncSession = Depends(get_db)
):
    exam_question = await exam_question_crud.get_by_ids(db, exam_id, question_id)
    if not exam_question:
        raise HTTPException(status_code=404, detail="Exam question not found")
    return exam_question


@router.post(
    "/",
    response_model=ExamQuestionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:create")),
    ],
)
async def create_exam_question(
    obj_in: ExamQuestionCreate, db: AsyncSession = Depends(get_db)
):
    return await exam_question_crud.create(db, obj_in)


@router.put(
    "/{exam_id}/{question_id}",
    response_model=ExamQuestionRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:update")),
    ],
)
async def update_exam_question(
    exam_id: int,
    question_id: int,
    obj_in: ExamQuestionUpdate,
    db: AsyncSession = Depends(get_db),
):
    exam_question = await exam_question_crud.get_by_ids(db, exam_id, question_id)
    if not exam_question:
        raise HTTPException(status_code=404, detail="Exam question not found")
    return await exam_question_crud.update(db, exam_question, obj_in)


@router.delete(
    "/{exam_id}/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:delete")),
    ],
)
async def delete_exam_question(
    exam_id: int, question_id: int, db: AsyncSession = Depends(get_db)
):
    await exam_question_crud.delete(db, exam_id, question_id)
    return None
