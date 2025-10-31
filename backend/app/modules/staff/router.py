from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.staff.schemas import StaffCreate, StaffRead, StaffUpdate
from app.modules.staff.crud import staff_crud

staff_router = APIRouter(prefix="/staff", tags=["Staff"])


@staff_router.get("/", response_model=List[StaffRead])
async def list_staff(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    return await staff_crud.get_all(db)


@staff_router.get("/{staff_id}", response_model=StaffRead)
async def get_staff(
    staff_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    staff = await staff_crud.get_by_id(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff


@staff_router.post(
    "/",
    response_model=StaffRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff:create")),
    ],
)
async def create_staff(staff_in: StaffCreate, db: AsyncSession = Depends(get_db)):
    return await staff_crud.create(db, staff_in)


@staff_router.put(
    "/{staff_id}",
    response_model=StaffRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff:update")),
    ],
)
async def update_staff(
    staff_id: int, staff_in: StaffUpdate, db: AsyncSession = Depends(get_db)
):
    staff = await staff_crud.get_by_id(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return await staff_crud.update(db, staff, staff_in)


@staff_router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff:delete")),
    ],
)
async def delete_staff(staff_id: int, db: AsyncSession = Depends(get_db)):
    await staff_crud.delete(db, staff_id)
    return None
