# # backend/app/modules/users/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.users.schemas import UserCreate, UserRead, UserUpdate, UserStatus
from app.modules.users.crud import user_crud

router = APIRouter(prefix="/users", tags=["Admin Users"])


@router.get(
    "/",
    response_model=List[UserRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:view")),
    ],
)
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_all(db)


@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:view")),
    ],
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:create")),
    ],
)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await user_crud.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_crud.create(db, user_in)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:create")),
    ],
)
async def register_user_admin(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Admin-only endpoint for registering staff or manager users.
    """
    existing = await user_crud.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Default status pending for new admin/staff user
    user_in.status = UserStatus.pending
    return await user_crud.create(db, user_in)


@router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:update")),
    ],
)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.update(db, user, user_in)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:delete")),
    ],
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    await user_crud.delete(db, user_id)
    return None


@router.put(
    "/{user_id}/approve",
    response_model=UserRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("user:approve")),
    ],
)
async def approve_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = UserStatus.active
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
