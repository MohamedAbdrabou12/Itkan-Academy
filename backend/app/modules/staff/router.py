# backend/app/modules/staff/router.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.staff.schemas import StaffCreate, StaffRead, StaffUpdate
from app.modules.staff.service import StaffService
from app.modules.users.models import User

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


@staff_router.get(
    "/",
    response_model=List[StaffRead],
    dependencies=[Depends(require_permission("staff:view"))],
)
async def list_staff(db: AsyncSession = Depends(get_db)):
    return await StaffService.list_staff(db)


@staff_router.get(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff:view"))],
)
async def get_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    return await StaffService.get_staff(db, staff_id)


@staff_router.post(
    "/",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("staff:create"))],
)
async def create_staff(
    staff_in: StaffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StaffService.create_staff(db, staff_in, current_user)


@staff_router.put(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff:update"))],
)
async def update_staff(
    staff_id: int, staff_in: StaffUpdate, db: AsyncSession = Depends(get_db)
):
    return await StaffService.update_staff(db, staff_id, staff_in)


@staff_router.delete(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff:delete"))],
)
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    return await StaffService.delete_staff(db, staff_id)


@staff_router.post(
    "/{staff_id}/approve",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff:update"))],
)
async def approve_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StaffService.approve_staff(db, staff_id, current_user)


@staff_router.post(
    "/{staff_id}/reject",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff:update"))],
)
async def reject_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StaffService.reject_staff(db, staff_id, current_user)
