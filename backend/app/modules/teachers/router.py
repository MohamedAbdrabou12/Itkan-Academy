# backend/app/modules/teachers/router.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.teachers.schemas import TeacherCreate, TeacherRead, TeacherUpdate
from app.modules.teachers.service import TeacherService
from app.modules.users.models import User

teachers_router = APIRouter(prefix="/teachers", tags=["Teachers"])


@teachers_router.get(
    "/",
    response_model=List[TeacherRead],
    dependencies=[Depends(require_permission("teacher:view"))],
)
async def list_teachers(db: AsyncSession = Depends(get_db)):
    return await TeacherService.list_teachers(db)


@teachers_router.get(
    "/{teacher_id}",
    response_model=TeacherRead,
    dependencies=[Depends(require_permission("teacher:view"))],
)
async def get_teacher(teacher_id: int, db: AsyncSession = Depends(get_db)):
    return await TeacherService.get_teacher(db, teacher_id)


@teachers_router.post(
    "/",
    response_model=TeacherRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("teacher:create"))],
)
async def create_teacher(
    teacher_in: TeacherCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await TeacherService.create_teacher(db, teacher_in, current_user)


@teachers_router.put(
    "/{teacher_id}",
    response_model=TeacherRead,
    dependencies=[Depends(require_permission("teacher:update"))],
)
async def update_teacher(
    teacher_id: int,
    teacher_in: TeacherUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await TeacherService.update_teacher(db, teacher_id, teacher_in)


@teachers_router.delete(
    "/{teacher_id}",
    response_model=TeacherRead,
    dependencies=[Depends(require_permission("teacher:delete"))],
)
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await TeacherService.delete_teacher(db, teacher_id)


@teachers_router.post(
    "/{teacher_id}/approve",
    response_model=TeacherRead,
    dependencies=[Depends(require_permission("teacher:update"))],
)
async def approve_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await TeacherService.approve_teacher(db, teacher_id, current_user)


@teachers_router.post(
    "/{teacher_id}/reject",
    response_model=TeacherRead,
    dependencies=[Depends(require_permission("teacher:update"))],
)
async def reject_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await TeacherService.reject_teacher(db, teacher_id, current_user)
