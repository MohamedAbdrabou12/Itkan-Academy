# # app/modules/roles/crud.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.roles.models import Role
from app.modules.roles.schemas import RoleCreate, RoleUpdate


class RoleCRUD:
    async def get_all(self, db: AsyncSession) -> List[Role]:
        result = await db.execute(
            select(Role).options(
                selectinload(Role.permissions),
            )
        )
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, role_id: int) -> Optional[Role]:
        result = await db.execute(
            select(Role)
            .where(Role.id == role_id)
            .options(
                selectinload(Role.permissions),
            )
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: RoleCreate) -> Role:
        db_obj = Role(
            name=obj_in.name,
            description=obj_in.description,
        )
        db.add(db_obj)
        await db.flush()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, db_obj: Role, obj_in: RoleUpdate) -> Role:
        data = obj_in.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, role_id: int) -> None:
        role = await self.get_by_id(db, role_id)
        if role:
            await db.delete(role)
            await db.commit()


role_crud = RoleCRUD()
