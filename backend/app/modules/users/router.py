from typing import Optional

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.roles.crud import role_crud
from app.modules.users.crud import map_user_to_read, user_crud
from app.modules.users.models import UserStatus
from app.modules.users.schemas import UserCreate, UserRead, UserRoleUpdate, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "/",
    response_model=Page[UserRead],
    dependencies=[
        # Depends(get_current_user),
        # Depends(require_permission("staff.management.manage")),
    ],
)
async def list_users(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("id"),
    sort_order: Optional[str] = Query("asc"),
):
    return await user_crud.get_all(
        db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@user_router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff.management.manage")),
    ],
)
async def get_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Get single user, applying branch filter for non-admins.
    """
    user = await user_crud.get_by_id(db, user_id, request)
    if not user:
        return None
    return map_user_to_read(user)


@user_router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff.management.manage")),
    ],
)
async def create_user(
    user_in: UserCreate, request: Request, db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    - Prevent normal users from assigning unauthorized branch_ids.
    - Admins can assign any branch.
    """
    current_user = request.state.current_user  # assuming middleware sets current user
    is_admin = current_user.role_name == "admin"

    # Verify branch_ids for non-admin users
    if not is_admin and user_in.branch_ids:
        allowed_branches = getattr(request.state, "branch_ids", [])
        invalid_ids = [bid for bid in user_in.branch_ids if bid not in allowed_branches]
        if invalid_ids:
            raise HTTPException(
                status_code=403, detail=f"You cannot assign branches: {invalid_ids}"
            )

    existing = await user_crud.get_by_email(db, user_in.email)
    if existing:
        return map_user_to_read(existing)

    # pass request if needed inside crud for future branch filtering
    user = await user_crud.create(db, user_in)
    if not user:
        return None
    return map_user_to_read(user)


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
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("staff.management.manage")),
    ],
)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Update existing user.
    - Verify branch_ids for non-admin users.
    """
    current_user = request.state.current_user
    is_admin = current_user.role_name == "admin"

    user = await user_crud.get_by_id(db, user_id)
    if not user:
        return None

    # Verify branch_ids if updating them
    if not is_admin and user_in.branch_ids:
        allowed_branches = getattr(request.state, "branch_ids", [])
        invalid_ids = [bid for bid in user_in.branch_ids if bid not in allowed_branches]
        if invalid_ids:
            raise HTTPException(
                status_code=403, detail=f"You cannot assign branches: {invalid_ids}"
            )

    user = await user_crud.update(db, user, user_in)
    return map_user_to_read(user)


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
