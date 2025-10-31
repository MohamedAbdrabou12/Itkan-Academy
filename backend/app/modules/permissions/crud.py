from typing import List, Optional

from app.modules.permissions.models import Permission
from app.modules.permissions.schemas import (
    PermissionCreate,
    PermissionUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class PermissionCRUD:
    async def get_all(self, db: AsyncSession) -> List[Permission]:
        result = await db.execute(select(Permission))
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, permission_id: int
    ) -> Optional[Permission]:
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalars().first()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Permission]:
        result = await db.execute(select(Permission).where(Permission.code == code))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: PermissionCreate) -> Permission:
        db_obj = Permission(code=obj_in.code, description=obj_in.description)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: Permission, obj_in: PermissionUpdate
    ) -> Permission:
        data = obj_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, permission_id: int) -> bool:
        permission = await self.get_by_id(db, permission_id)
        if permission:
            await db.delete(permission)
            await db.commit()
            return True
        return False


permission_crud = PermissionCRUD()
