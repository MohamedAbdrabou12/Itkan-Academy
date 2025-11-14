from typing import List, Optional

from app.modules.permissions.models import Permission
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PermissionCRUD:
    async def get_all_permissions(self, db: AsyncSession) -> List[Permission]:
        result = await db.execute(select(Permission))
        return list(result.scalars().all())

    async def get_permission(
        self, db: AsyncSession, permission_id: int
    ) -> Optional[Permission]:
        result = await db.execute(
            select(Permission).filter(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()


permission_crud = PermissionCRUD()
