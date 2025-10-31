from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.exams.schemas.exam_answer import (
    ExamAnswerCreate,
    ExamAnswerUpdate,
    ExamAnswerRead,
)
from app.modules.exams.crud.exam_answer import exam_answer_crud

router = APIRouter(prefix="/exam-answers", tags=["Exam Answers"])


@router.get(
    "/",
    response_model=List[ExamAnswerRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def list_exam_answers(db: AsyncSession = Depends(get_db)):
    return await exam_answer_crud.get_all(db)


@router.get(
    "/{answer_id}",
    response_model=ExamAnswerRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def get_exam_answer(answer_id: int, db: AsyncSession = Depends(get_db)):
    answer = await exam_answer_crud.get_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Exam answer not found")
    return answer


@router.post(
    "/",
    response_model=ExamAnswerRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:create")),
    ],
)
async def create_exam_answer(
    obj_in: ExamAnswerCreate, db: AsyncSession = Depends(get_db)
):
    return await exam_answer_crud.create(db, obj_in)


@router.put(
    "/{answer_id}",
    response_model=ExamAnswerRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:update")),
    ],
)
async def update_exam_answer(
    answer_id: int,
    obj_in: ExamAnswerUpdate,
    db: AsyncSession = Depends(get_db),
):
    answer = await exam_answer_crud.get_by_id(db, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="Exam answer not found")
    return await exam_answer_crud.update(db, answer, obj_in)


@router.delete(
    "/{answer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:delete")),
    ],
)
async def delete_exam_answer(answer_id: int, db: AsyncSession = Depends(get_db)):
    await exam_answer_crud.delete(db, answer_id)
    return None
