from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.modules.users.models import User
from app.modules.exams.schemas.exam import ExamCreate, ExamRead, ExamUpdate
from app.modules.exams.services import exam_service

exam_router = APIRouter(prefix="/exams", tags=["Exams"])


@exam_router.post("/", response_model=ExamRead, status_code=status.HTTP_201_CREATED)
async def create_exam(
    exam_in: ExamCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.create_exam(db, exam_in=exam_in, user=user)


@exam_router.get("/", response_model=List[ExamRead])
async def list_exams(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    exams = await exam_service.get_all_exams(db, user)
    if not exams:
        return []
    return exams


@exam_router.get("/{exam_id}", response_model=ExamRead)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.get_exam(db, id=exam_id, user=user)


@exam_router.put("/{exam_id}", response_model=ExamRead)
async def update_exam(
    exam_id: int,
    exam_in: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.update_exam(db, id=exam_id, exam_in=exam_in, user=user)


@exam_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await exam_service.delete_exam(db, id=exam_id, user=user)
    return


@exam_router.post("/{exam_id}/publish", response_model=ExamRead)
async def publish_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.publish_exam(db, id=exam_id, user=user)


@exam_router.post("/{exam_id}/close", response_model=ExamRead)
async def close_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.close_exam(db, id=exam_id, user=user)
