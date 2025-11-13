from typing import List

from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.exams.crud.exam_answer import exam_answer_crud
from app.modules.exams.crud.exam_attempt import exam_attempt_crud
from app.modules.exams.schemas.exam_answer import (
    ExamAnswerBulkCreate,
    ExamAnswerRead,
    ExamAnswerResponse,
)
from app.modules.exams.services import exam_answers_service
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

exam_answers_router = APIRouter(prefix="/exam-answers", tags=["Exam Answers"])


@exam_answers_router.get(
    "/",
    response_model=List[ExamAnswerResponse],
)
async def list_answers(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Logic to check if user can view answers for this attempt
    attempt = await exam_attempt_crud.get_with_user(db, attempt_id, current_user)
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")

    # TODO: permission check

    return await exam_answer_crud.get_multi_by_attempt(db, attempt_id=attempt_id)


@exam_answers_router.post(
    "/bulk",
    response_model=List[ExamAnswerRead],
    status_code=status.HTTP_201_CREATED,
)
async def submit_answers_bulk(
    attempt_id: int,
    answers_in: ExamAnswerBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await exam_answers_service.submit_answers_bulk(
        db, attempt_id=attempt_id, answers_in=answers_in, user=current_user
    )


# @exam_answers_router.put(
#     "/{id}",
#     response_model=ExamAnswerRead,
#     dependencies=[Depends(require_permission("exam_answer:edit"))],
# )
# async def update_answer(
#     id: int,
#     answer_in: ExamAnswerUpdate,
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     db_obj = await exam_answer_crud.get(db, id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="Exam answer not found")
#     # Logic to check if user can update this answer (student before submit, or teacher for grading)
#     return await exam_answer_crud.update(db, db_obj=db_obj, obj_in=answer_in)


# @exam_answers_router.delete(
#     "/{id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_permission("exam_answer:delete"))],
# )
# async def delete_answer(id: int, db: AsyncSession = Depends(get_db)):
#     db_obj = await exam_answer_crud.delete(db, id=id)
#     if not db_obj:
#         raise HTTPException(status_code=404, detail="Exam answer not found")
#     return
