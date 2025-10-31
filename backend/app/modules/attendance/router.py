from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceRead,
    AttendanceUpdate,
)
from app.modules.attendance.crud import attendance_crud

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.get("/", response_model=List[AttendanceRead])
async def list_attendance(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await attendance_crud.get_all(db)


@router.get("/{attendance_id}", response_model=AttendanceRead)
async def get_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    attendance = await attendance_crud.get_by_id(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.post(
    "/",
    response_model=AttendanceRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("attendance:create")),
    ],
)
async def create_attendance(
    attendance_in: AttendanceCreate, db: AsyncSession = Depends(get_db)
):
    return await attendance_crud.create(db, attendance_in)


@router.put(
    "/{attendance_id}",
    response_model=AttendanceRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("attendance:update")),
    ],
)
async def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    attendance = await attendance_crud.get_by_id(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return await attendance_crud.update(db, attendance, attendance_in)


@router.delete(
    "/{attendance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("attendance:delete")),
    ],
)
async def delete_attendance(attendance_id: int, db: AsyncSession = Depends(get_db)):
    await attendance_crud.delete(db, attendance_id)
    return None
