from typing import List

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.evaluations.crud import daily_evaluation_crud
from app.modules.evaluations.schemas import (
    DailyEvaluationCreate,
    DailyEvaluationRead,
    DailyEvaluationUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

daily_evaluation_router = APIRouter(
    prefix="/daily-evaluations", tags=["Daily Evaluations"]
)


@daily_evaluation_router.get("/", response_model=List[DailyEvaluationRead])
async def list_evaluations(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await daily_evaluation_crud.get_all(db)


@daily_evaluation_router.get("/{eval_id}", response_model=DailyEvaluationRead)
async def get_evaluation(
    eval_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    evaluation = await daily_evaluation_crud.get_by_id(db, eval_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Daily evaluation not found")
    return evaluation


@daily_evaluation_router.post(
    "/",
    response_model=DailyEvaluationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("evaluation:create")),
    ],
)
async def create_evaluation(
    eval_in: DailyEvaluationCreate, db: AsyncSession = Depends(get_db)
):
    return await daily_evaluation_crud.create(db, eval_in)


@daily_evaluation_router.put(
    "/{eval_id}",
    response_model=DailyEvaluationRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("evaluation:update")),
    ],
)
async def update_evaluation(
    eval_id: int, eval_in: DailyEvaluationUpdate, db: AsyncSession = Depends(get_db)
):
    evaluation = await daily_evaluation_crud.get_by_id(db, eval_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Daily evaluation not found")
    return await daily_evaluation_crud.update(db, evaluation, eval_in)


@daily_evaluation_router.delete(
    "/{eval_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("evaluation:delete")),
    ],
)
async def delete_evaluation(eval_id: int, db: AsyncSession = Depends(get_db)):
    await daily_evaluation_crud.delete(db, eval_id)
    return None
