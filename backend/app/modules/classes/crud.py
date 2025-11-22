# backend/app/modules/classes/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.modules.classes.models import Class
from app.modules.classes.schemas import ClassCreate, ClassUpdate


class ClassCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        branch_id: int | None = None,
    ) -> List[Class]:
        stmt = select(Class).order_by(Class.id)
        if branch_id is not None:
            stmt = stmt.where(Class.branch_id == branch_id)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, class_id: int, branch_id: int | None = None
    ) -> Optional[Class]:
        stmt = select(Class).where(Class.id == class_id)
        if branch_id is not None:
            stmt = stmt.where(Class.branch_id == branch_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, class_in: ClassCreate) -> Class:
        class_ = Class(**class_in.dict())
        db.add(class_)
        await db.commit()
        await db.refresh(class_)
        return class_

    async def update(
        self, db: AsyncSession, class_: Class, class_in: ClassUpdate
    ) -> Class:
        for field, value in class_in.dict(exclude_unset=True).items():
            setattr(class_, field, value)
        db.add(class_)
        await db.commit()
        await db.refresh(class_)
        return class_

    async def delete(self, db: AsyncSession, class_id: int) -> None:
        class_ = await self.get_by_id(db, class_id)
        if class_:
            await db.delete(class_)
            await db.commit()


class_crud = ClassCRUD()
