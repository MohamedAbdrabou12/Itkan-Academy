from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.question_bank.schemas import (
    QuestionBankCreate,
    QuestionBankRead,
    QuestionBankUpdate,
)
from app.modules.question_bank.crud import question_bank_crud

question_bank_router = APIRouter(prefix="/question-bank", tags=["Question Bank"])


@question_bank_router.get(
    "/",
    response_model=List[QuestionBankRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("question:view")),
    ],
)
async def list_questions(db: AsyncSession = Depends(get_db)):
    return await question_bank_crud.get_all(db)


@question_bank_router.get(
    "/{question_id}",
    response_model=QuestionBankRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("question:view")),
    ],
)
async def get_question(question_id: int, db: AsyncSession = Depends(get_db)):
    question = await question_bank_crud.get_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@question_bank_router.post(
    "/",
    response_model=QuestionBankRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("question:create")),
    ],
)
async def create_question(
    question_in: QuestionBankCreate, db: AsyncSession = Depends(get_db)
):
    return await question_bank_crud.create(db, question_in)


@question_bank_router.put(
    "/{question_id}",
    response_model=QuestionBankRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("question:update")),
    ],
)
async def update_question(
    question_id: int,
    question_in: QuestionBankUpdate,
    db: AsyncSession = Depends(get_db),
):
    question = await question_bank_crud.get_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return await question_bank_crud.update(db, question, question_in)


@question_bank_router.delete(
    "/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("question:delete")),
    ],
)
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db)):
    await question_bank_crud.delete(db, question_id)
    return None
