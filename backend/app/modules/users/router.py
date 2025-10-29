from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.users.schemas import UserCreate, UserRead, UserUpdate
from app.modules.users.crud import user_crud

router = APIRouter(prefix="/users", tags=["Users"])


# List all users
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


# Get a single user by ID
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


# Create a new user
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


# Update user information
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


# Delete user by ID
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
