from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.exams.schemas.exam_attempt import (
    ExamAttemptCreate,
    ExamAttemptUpdate,
    ExamAttemptRead,
)
from app.modules.exams.crud.exam_attempt import exam_attempt_crud

exam_attempt_router = APIRouter(prefix="/exam-attempts", tags=["Exam Attempts"])


@exam_attempt_router.get(
    "/",
    response_model=List[ExamAttemptRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def list_exam_attempts(db: AsyncSession = Depends(get_db)):
    return await exam_attempt_crud.get_all(db)


@exam_attempt_router.get(
    "/{attempt_id}",
    response_model=ExamAttemptRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("exam:view"))],
)
async def get_exam_attempt(attempt_id: int, db: AsyncSession = Depends(get_db)):
    attempt = await exam_attempt_crud.get_by_id(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    return attempt


@exam_attempt_router.post(
    "/",
    response_model=ExamAttemptRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:create")),
    ],
)
async def create_exam_attempt(
    obj_in: ExamAttemptCreate, db: AsyncSession = Depends(get_db)
):
    return await exam_attempt_crud.create(db, obj_in)


@exam_attempt_router.put(
    "/{attempt_id}",
    response_model=ExamAttemptRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:update")),
    ],
)
async def update_exam_attempt(
    attempt_id: int,
    obj_in: ExamAttemptUpdate,
    db: AsyncSession = Depends(get_db),
):
    attempt = await exam_attempt_crud.get_by_id(db, attempt_id)
    if not attempt:
        raise HTTPException(status_code=404, detail="Exam attempt not found")
    return await exam_attempt_crud.update(db, attempt, obj_in)


@exam_attempt_router.delete(
    "/{attempt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("exam:delete")),
    ],
)
async def delete_exam_attempt(attempt_id: int, db: AsyncSession = Depends(get_db)):
    await exam_attempt_crud.delete(db, attempt_id)
    return None
