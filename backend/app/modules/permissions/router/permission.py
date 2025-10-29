from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.modules.permissions.schemas.permission import (
    PermissionCreate,
    PermissionRead,
    PermissionUpdate,
)
from app.modules.permissions.crud.permission import permission_crud

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get(
    "/",
    response_model=List[PermissionRead],
    dependencies=[
        Depends(require_permission("permission:view")),
        Depends(get_current_user),
    ],
)
async def list_permissions(db: AsyncSession = Depends(get_db)) -> List[PermissionRead]:
    """Get all permissions."""
    return await permission_crud.get_all(db)


@router.get(
    "/{permission_id}",
    response_model=PermissionRead,
    dependencies=[
        Depends(require_permission("permission:view")),
        Depends(get_current_user),
    ],
)
async def get_permission(
    permission_id: int, db: AsyncSession = Depends(get_db)
) -> PermissionRead:
    """Get a specific permission by ID."""
    permission = await permission_crud.get_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.post(
    "/",
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("permission:create")),
        Depends(get_current_user),
    ],
)
async def create_permission(
    permission_in: PermissionCreate, db: AsyncSession = Depends(get_db)
) -> PermissionRead:
    """Create a new permission."""
    existing = await permission_crud.get_by_code(db, permission_in.code)
    if existing:
        raise HTTPException(status_code=400, detail="Permission code already exists")
    return await permission_crud.create(db, permission_in)


@router.put(
    "/{permission_id}",
    response_model=PermissionRead,
    dependencies=[
        Depends(require_permission("permission:update")),
        Depends(get_current_user),
    ],
)
async def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
) -> PermissionRead:
    """Update an existing permission."""
    permission = await permission_crud.get_by_id(db, permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return await permission_crud.update(db, permission, permission_in)


@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission("permission:delete")),
        Depends(get_current_user),
    ],
)
async def delete_permission(
    permission_id: int, db: AsyncSession = Depends(get_db)
) -> Response:
    """Delete a permission by ID."""
    deleted = await permission_crud.delete(db, permission_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Permission not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
