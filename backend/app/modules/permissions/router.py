from typing import List

from app.db.session import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import permission_crud
from .schemas import (
    Permission,
)

permissions_router = APIRouter(prefix="/permissions", tags=["Permissions"])

@permissions_router.get("/", response_model=List[Permission])
async def get_permissions(db: AsyncSession = Depends(get_db)):
    available_permissions_db = await permission_crud.get_all_permissions(db)

    # Convert available permissions to Pydantic schemas
    available_permissions = [
        Permission.model_validate(perm) for perm in available_permissions_db
    ]

    return available_permissions

