# app/modules/users/router.py
from typing import Optional
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.roles.crud import role_crud
from app.modules.users.crud import map_user_to_read, user_crud
from app.modules.users.models import UserStatus
from app.modules.users.schemas import UserCreate, UserRead, UserRoleUpdate, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/staff",
    response_model=Page[UserRead],
    dependencies=[
        Depends(require_permission(PermissionCode.SYSTEM_STAFF_VIEW)),
    ],
)
async def list_all_staff(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
):
    return await user_crud.get_all_staff(
        db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@user_router.post(
    "/staff",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission(PermissionCode.SYSTEM_STAFF_ADD)),
    ],
)
async def create_staff(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await user_crud.create(db, user)


@user_router.patch(
    "/role",
    response_model=UserRead,
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("user.management.update")),
    ],
)
async def update_user_role(
    role_update: UserRoleUpdate, db: AsyncSession = Depends(get_db)
):
    # Check if user exists
    existing_user = await user_crud.get_by_id(db, role_update.user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Check if role exists (optional but recommended)
    existing_role = await role_crud.get_by_id(db, role_update.role_id)
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    # Update user role
    updated_user = await user_crud.update_role(db, existing_user, role_update.role_id)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role",
        )

    return map_user_to_read(updated_user)


@user_router.put(
    "/staff/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission(PermissionCode.SYSTEM_STAFF_EDIT)),
    ],
)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return await user_crud.update(db, user, user_update)


@user_router.delete(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff.management.manage")),
    ],
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Soft delete a user by setting status to deactive.
    """
    user = await user_crud.delete(db, user_id)
    if not user:
        return None
    return map_user_to_read(user)


@user_router.put(
    "/{user_id}/approve",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff.management.manage")),
    ],
)
async def approve_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Approve a pending user by setting status to active.
    """
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        return None
    user.status = UserStatus.active.value
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return map_user_to_read(user)
