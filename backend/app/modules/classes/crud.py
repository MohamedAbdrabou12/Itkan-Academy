# backend/app/modules/classes/crud.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from fastapi import Request
from app.modules.classes.models import Class
from app.modules.classes.schemas import ClassCreate, ClassUpdate
from fastapi_pagination.ext.sqlalchemy import paginate


class ClassCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        request: Optional[Request] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> List[Class]:
        stmt = select(Class)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)

            if branch_id is not None:
                stmt = stmt.where(Class.branch_id == branch_id)
        # Search
        if search:
            stmt = stmt.where(Class.name.ilike(f"%{search}%"))

        # Apply sorting
        sort_column = getattr(Class, sort_by) if sort_by else Class.id
        if sort_order and sort_order.lower() == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        result = await paginate(db, stmt)
        return result

    async def get_class_by_branch(
        self,
        db: AsyncSession,
        branch_ids: list[int],
    ):
        stmt = select(Class).where(Class.branch_id.in_(branch_ids))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, class_id: int, request: Optional[Request] = None
    ) -> Optional[Class]:
        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                stmt = (
                    Class.__table__.select()
                    .where(Class.id == class_id)
                    .where(Class.branch_id == branch_id)
                )
                result = await db.execute(stmt)
                return result.scalars().first()

        return await db.get(Class, class_id)

    async def create(self, db: AsyncSession, class_in: ClassCreate) -> Class:
        class_ = Class(**class_in.model_dump())
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
