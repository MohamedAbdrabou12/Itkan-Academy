# backend/app/modules/question_bank/router.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.modules.question_bank.schemas import (
    QuestionBankCreate,
    QuestionBankRead,
)
from app.core.authorization import require_permission
from .service import question_bank_service
from app.modules.users.models import User


question_bank_router = APIRouter(prefix="/question-bank", tags=["Question Bank"])


@question_bank_router.get(
    "/",
    response_model=List[QuestionBankRead],
    # dependencies=[
    #     Depends(get_current_user),
    #     # Depends(require_permission("question:view")),
    # ],
)
async def list_questions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    with_shared: bool = False,
):
    return await question_bank_service.get_all_questions(db, user, with_shared)


@question_bank_router.get(
    "/{question_id}",
    response_model=QuestionBankRead,
    # dependencies=[
    #     Depends(get_current_user),
    #     Depends(require_permission("question:view")),
    # ],
)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    question = await question_bank_service.get_question_by_id(db, question_id, user)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@question_bank_router.post(
    "/",
    response_model=QuestionBankRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    request: Request,
    question_in: QuestionBankCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await question_bank_service.create_question(request, db, question_in, user)


@question_bank_router.put(
    "/{question_id}",
    response_model=QuestionBankRead,
    # dependencies=[
    #     Depends(get_current_user),
    #     Depends(require_permission("question:update")),
    # ],
)
async def update_question(
    question_id: int,
    question_in: QuestionBankCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await question_bank_service.update_question(
        db, question_id, question_in, user
    )


# @question_bank_router.delete(
#     "/{question_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[
#         Depends(get_current_user),
#         # Depends(require_permission("question:delete")),
#     ],
# )
# async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
#     await question_bank_crud.delete(db, question_id)
#     return None
