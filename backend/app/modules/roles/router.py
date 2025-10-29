from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission

from app.modules.roles.schemas import RoleCreate, RoleRead, RoleUpdate
from app.modules.roles.crud import role_crud

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get(
    "/",
    response_model=List[RoleRead],
    dependencies=[Depends(get_current_user), Depends(require_permission("role:view"))],
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    return await role_crud.get_all(db)


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[Depends(get_current_user), Depends(require_permission("role:view"))],
)
async def get_role(role_id: int, db: AsyncSession = Depends(get_db)):
    role = await role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.post(
    "/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role:create")),
    ],
)
async def create_role(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    return await role_crud.create(db, role_in)


@router.put(
    "/{role_id}",
    response_model=RoleRead,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role:update")),
    ],
)
async def update_role(
    role_id: int, role_in: RoleUpdate, db: AsyncSession = Depends(get_db)
):
    role = await role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return await role_crud.update(db, role, role_in)


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(get_current_user),
        Depends(require_permission("role:delete")),
    ],
)
async def delete_role(role_id: int, db: AsyncSession = Depends(get_db)):
    await role_crud.delete(db, role_id)
    return None
