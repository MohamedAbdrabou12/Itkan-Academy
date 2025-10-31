# app/modules/permissions/router/permission_role.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.permissions.schemas.permission_role import (
    RolePermissionCreate,
    RolePermissionRead,
)
from app.modules.permissions.crud.permission_role import role_permission_crud

router = APIRouter(prefix="/role-permissions", tags=["Role Permissions"])


@router.get(
    "/",
    response_model=List[RolePermissionRead],
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role_permission:view")),
    ],
)
async def list_role_permissions(db: AsyncSession = Depends(get_db)):
    return await role_permission_crud.get_all(db)


@router.post(
    "/",
    response_model=RolePermissionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role_permission:assign")),
    ],
)
async def assign_permission_to_role(
    payload: RolePermissionCreate, db: AsyncSession = Depends(get_db)
):
    created = await role_permission_crud.create(db, payload)
    if not created:
        raise HTTPException(
            status_code=400, detail="Failed to assign permission to role"
        )
    return created


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role_permission:remove")),
    ],
)
async def remove_permission_from_role(
    role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)
):
    deleted = await role_permission_crud.delete(db, role_id, permission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Role or Permission not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
