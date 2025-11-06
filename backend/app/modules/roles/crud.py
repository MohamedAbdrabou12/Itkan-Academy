from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_
from fastapi import Request

from app.modules.roles.models import Role
from app.modules.roles.schemas import RoleCreate, RoleUpdate


class RoleCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        request: Optional[Request] = None,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
    ) -> dict:
        # Build base query
        query = select(Role).options(selectinload(Role.permissions))

        # Apply search
        if search:
            search_filter = or_(
                Role.name.ilike(f"%{search}%"),
                Role.name_in_arabic.ilike(f"%{search}%"),
                Role.description.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                # Assuming Role model may have branch_id in future or skip if all roles global
                pass  # No branch filtering for now; placeholder

        # Get total count before pagination and sorting
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply sorting
        sort_column_name = sort_by or "id"
        sort_order_direction = sort_order or "asc"
        sort_column = getattr(Role, sort_column_name, Role.name)
        query = query.order_by(
            sort_column.desc()
            if sort_order_direction.lower() == "desc"
            else sort_column.asc()
        )

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        roles = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size

        return {
            "data": roles,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    async def get_by_id(
        self, db: AsyncSession, role_id: int, request: Optional[Request] = None
    ) -> Optional[Role]:
        stmt = (
            select(Role)
            .where(Role.id == role_id)
            .options(selectinload(Role.permissions))
        )

        # Branch scoping
        if request:
            branch_id = getattr(request.state, "branch_id", None)
            if branch_id is not None:
                # Roles are usually global; placeholder for future branch filtering
                pass

        result = await db.execute(stmt)
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: RoleCreate) -> Role:
        db_obj = Role(name=obj_in.name, description=obj_in.description)
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
