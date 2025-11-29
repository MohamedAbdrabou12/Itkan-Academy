from typing import Optional

from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.permissions.permissions import PermissionCode
from app.modules.roles.crud import role_crud
from app.modules.roles.schemas import (
    RoleCreate,
    RoleRead,
    RoleUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

role_router = APIRouter(prefix="/roles", tags=["Roles"])


@role_router.get(
    "/",
    response_model=Page[RoleRead],
)
async def list_roles(
    search: Optional[str] = Query(None, description="Search in name"),
    sort_by: Optional[str] = Query("id", description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order: asc or desc"),
    db: AsyncSession = Depends(get_db),
    _=[Depends(require_permission(PermissionCode.SYSTEM_ROLES_VIEW))],
):
    return await role_crud.get_all(
        db=db,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@role_router.get(
    "/{role_id}",
    response_model=RoleRead,
)
async def get_role(
    role_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _=[Depends(require_permission(PermissionCode.SYSTEM_ROLES_VIEW))],
):
    role = await role_crud.get_by_id(db, role_id, request)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@role_router.post(
    "/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _=[Depends(require_permission(PermissionCode.SYSTEM_ROLES_ADD))],
):
    return await role_crud.create(db, role_in)


@role_router.put(
    "/{role_id}",
    response_model=RoleRead,
)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _=[Depends(require_permission(PermissionCode.SYSTEM_ROLES_EDIT))],
):
    role = await role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return await role_crud.update(db, role, role_in)


@role_router.delete(
    "/{role_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _=[Depends(require_permission(PermissionCode.SYSTEM_ROLES_DELETE))],
):
    await role_crud.delete(db, role_id)
    return {"detail": "Role deleted"}
