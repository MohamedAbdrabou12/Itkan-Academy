from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.students.schemas import StudentCreate, StudentRead, StudentUpdate
from app.modules.students.crud import student_crud

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/", response_model=List[StudentRead])
async def list_students(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await student_crud.get_all(db)


@router.get("/{student_id}", response_model=StudentRead)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    student = await student_crud.get_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post(
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


@router.put(
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


@router.delete(
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
