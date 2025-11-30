from typing import Optional

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.staff.crud import staff_crud
from app.modules.staff.schemas import StaffCreate, StaffRead, StaffUpdate
from app.modules.staff.service import StaffService
from app.modules.users.models import User
from app.modules.users.schemas import UserRead
from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


@staff_router.get(
    "/",
    response_model=Page[UserRead],
)
async def list_staff(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
    _=[Depends(require_permission(PermissionCode.SYSTEM_STAFF_VIEW))],
):
    return await staff_crud.get_all(
        db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@staff_router.get(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff.management.manage"))],
)
async def get_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    return await StaffService.get_staff(db, staff_id)


@staff_router.post(
    "/",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("staff.management.manage"))],
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
    dependencies=[Depends(require_permission("staff.management.manage"))],
)
async def update_staff(
    staff_id: int, staff_in: StaffUpdate, db: AsyncSession = Depends(get_db)
):
    return await StaffService.update_staff(db, staff_id, staff_in)


@staff_router.delete(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff.management.manage"))],
)
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    return await StaffService.delete_staff(db, staff_id)


@staff_router.post(
    "/{staff_id}/approve",
    response_model=StaffRead,
    dependencies=[Depends(require_permission("staff.management.manage"))],
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
    dependencies=[Depends(require_permission("staff.management.manage"))],
)
async def reject_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await StaffService.reject_staff(db, staff_id, current_user)
