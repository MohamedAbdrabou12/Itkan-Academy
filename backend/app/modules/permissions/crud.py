# backend/app/modules/permissions/crud.py
from typing import List, Optional
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.permissions.models import Permission
from app.modules.permissions.schemas import PermissionCreate, PermissionUpdate


class PermissionCRUD:
    async def get_all(
        self, db: AsyncSession, request: Optional[Request] = None
    ) -> List[Permission]:
        query = select(Permission)

        # Branch scoping placeholder
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                # Permissions are usually global; placeholder for future branch filtering
                pass

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, permission_id: int, request: Optional[Request] = None
    ) -> Optional[Permission]:
        stmt = select(Permission).where(Permission.id == permission_id)

        # Branch scoping placeholder
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                pass

        result = await db.execute(stmt)
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
