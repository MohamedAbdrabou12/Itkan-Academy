# backend/app/modules/role_permissions/crud.py
from typing import List, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.role_permissions.models import RolePermission
from app.modules.role_permissions.schemas import RolePermissionCreate


class RolePermissionCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[RolePermission]:
        query = select(RolePermission).options(
            selectinload(RolePermission.role),
            selectinload(RolePermission.permission),
        )

        # Branch scoping placeholder
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                # Currently all role-permissions are global; placeholder for branch filtering
                pass

        result = await db.execute(query)
        return result.scalars().all()

    async def create(
        self, db: AsyncSession, obj_in: RolePermissionCreate
    ) -> Optional[RolePermission]:
        db_obj = RolePermission(
            role_id=obj_in.role_id, permission_id=obj_in.permission_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, role_id: int, permission_id: int) -> bool:
        result = await db.execute(
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)
        )
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
            return True
        return False


role_permission_crud = RolePermissionCRUD()
