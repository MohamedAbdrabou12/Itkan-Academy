from fastapi import APIRouter, Depends, Query, Request, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.modules.users.models import User
from app.modules.exams.schemas.exam import (
    AvailableExams,
    ExamCreate,
    ExamRead,
    ExamUpdate,
    TakeExamRead,
)
from app.modules.exams.services import exam_service
from fastapi_pagination import Page

exam_router = APIRouter(prefix="/exams", tags=["Exams"])


@exam_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_exam(
    exam_in: ExamCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.create_exam(
        db, exam_in=exam_in, user=user, request=request
    )


@exam_router.get("/", response_model=Page[ExamRead])
async def list_exams(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search in name"),
    sort_by: Optional[str] = Query("id", description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
):
    exams = await exam_service.get_all_exams(
        db, user, request, search, sort_by, sort_order
    )
    if not exams:
        return []
    return exams


@exam_router.get("/available-exams", response_model=list[AvailableExams])
async def get_available_exams(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.get_available_exams(db, user)


@exam_router.get("/take/{exam_id}", response_model=TakeExamRead)
async def get_take_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.get_take_exam(db, user, exam_id)


@exam_router.get("/{exam_id}", response_model=ExamRead)
async def get_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.get_exam(db, id=exam_id, user=user)


@exam_router.put("/{exam_id}")
async def update_exam(
    exam_id: int,
    request: Request,
    exam_in: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await exam_service.update_exam(
        db, id=exam_id, exam_in=exam_in, user=user, request=request
    )


@exam_router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await exam_service.delete_exam(db, id=exam_id, user=user)
    return


@exam_router.post("/{exam_id}/publish")
async def publish_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.publish_exam(db, id=exam_id, user=user)


@exam_router.post("/{exam_id}/close")
async def close_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await exam_service.close_exam(db, id=exam_id, user=user)
