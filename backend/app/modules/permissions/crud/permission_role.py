# app/modules/permissions/crud/permission_role.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.permissions.models.permission_role import RolePermission
from app.modules.permissions.schemas.permission_role import RolePermissionCreate


class RolePermissionCRUD:
    async def get_all(self, db: AsyncSession) -> List[RolePermission]:
        result = await db.execute(
            select(RolePermission).options(
                selectinload(RolePermission.role),
                selectinload(RolePermission.permission),
            )
        )
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
