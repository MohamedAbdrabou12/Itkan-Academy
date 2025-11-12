from app.db.session import get_db
from app.modules.roles.crud import role_crud
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import permission_crud
from .schemas import (
    Permission,
    PermissionUpdateRequest,
    RolePermissionResponse,
    RolePermissionsResponse,
)

permissions_router = APIRouter(
    prefix="/roles/{role_id}/permissions", tags=["permissions"]
)


@permissions_router.get("", response_model=RolePermissionsResponse)
async def get_role_permissions(role_id: int, db: AsyncSession = Depends(get_db)):
    # Check if role exists
    role = await role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    # Get role permissions (permissions are already loaded via selectinload)
    role_permissions_db = await permission_crud.get_role_permissions(db, role_id)

    # Get all available permissions
    available_permissions_db = await permission_crud.get_all_permissions(db)

    # Convert SQLAlchemy models to Pydantic schemas
    role_permissions = []
    for rp_db in role_permissions_db:
        # Convert Permission SQLAlchemy model to Pydantic Permission schema
        permission_schema = (
            Permission.model_validate(rp_db.permission) if rp_db.permission else None
        )

        role_permission = RolePermissionResponse(
            role_id=rp_db.role_id,
            permission_id=rp_db.permission_id,
            permission_data=permission_schema,
        )
        role_permissions.append(role_permission)

    # Convert available permissions to Pydantic schemas
    available_permissions = [
        Permission.model_validate(perm) for perm in available_permissions_db
    ]

    return RolePermissionsResponse(
        role_permissions=role_permissions,
        available_permissions=available_permissions,
    )


@permissions_router.post("")
async def update_role_permissions(
    role_id: int,
    permission_request: PermissionUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    # Check if role exists
    role = await role_crud.get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )

    try:
        # Sync permissions
        updated_role_permissions = await permission_crud.sync_role_permissions(
            db, role_id, permission_request.permission_ids
        )

        response_data = {
            "success": True,
            "role_id": role_id,
            "assigned_permissions": [
                {
                    "permission_id": rp.permission_id,
                    "permission_code": rp.permission.code if rp.permission else None,
                    "permission_name_ar": rp.permission.name_ar
                    if rp.permission
                    else None,
                }
                for rp in updated_role_permissions
            ],
            "total_assigned": len(updated_role_permissions),
        }

        return response_data

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update permissions: {str(e)}",
        )
