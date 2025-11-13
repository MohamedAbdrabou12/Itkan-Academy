# backend/app/modules/students/router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.students.schemas import StudentCreate, StudentRead, StudentUpdate
from app.modules.students.service import StudentService
from app.modules.users.models import User

students_router = APIRouter(prefix="/students", tags=["Students"])


@students_router.get(
    "/",
    response_model=List[StudentRead],
    dependencies=[Depends(require_permission("student:view"))],
)
async def list_students(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter students by user status"),
):
    return await StudentService.list_students(db, status)


@students_router.get(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student:view"))],
)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    return await StudentService.get_student(db, student_id)


@students_router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("student:create"))],
)
async def create_student(
    student_in: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.create_student(db, student_in, current_user)


@students_router.put(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student:update"))],
)
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.update_student(db, student_id, student_in)


@students_router.delete(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student:delete"))],
)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    return await StudentService.delete_student(db, student_id)


@students_router.post(
    "/{student_id}/approve",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student:update"))],
)
async def approve_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.approve_student(db, student_id, current_user)


@students_router.post(
    "/{student_id}/reject",
    response_model=StudentRead,
    dependencies=[Depends(require_permission("student:update"))],
)
async def reject_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StudentService.reject_student(db, student_id, current_user)
