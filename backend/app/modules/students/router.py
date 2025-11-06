# backend/app/modules/students/router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.students.crud import student_crud
from app.modules.students.schemas import StudentCreate, StudentRead, StudentUpdate

students_router = APIRouter(prefix="/students", tags=["Students"])


@students_router.get(
    "/",
    response_model=List[StudentRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("student:view")),
    ],
)
async def list_students(request: Request, db: AsyncSession = Depends(get_db)):
    return await student_crud.get_all(db, request)


@students_router.get(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("student:view")),
    ],
)
async def get_student(
    student_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    student = await student_crud.get_by_id(db, student_id, request)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@students_router.post(
    "/",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("student:create")),
    ],
)
async def create_student(student_in: StudentCreate, db: AsyncSession = Depends(get_db)):
    return await student_crud.create(db, student_in)


@students_router.put(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("student:update")),
    ],
)
async def update_student(
    student_id: int, student_in: StudentUpdate, db: AsyncSession = Depends(get_db)
):
    student = await student_crud.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await student_crud.update(db, student, student_in)


@students_router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("student:delete")),
    ],
)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    await student_crud.delete(db, student_id)
    return None
