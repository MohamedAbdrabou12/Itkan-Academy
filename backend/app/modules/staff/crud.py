from typing import List, Optional

from app.modules.staff.models import Staff
from app.modules.users.models import User, UserBranch, UserStatus
from fastapi import HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import asc, desc, or_
from sqlalchemy import delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload


class StaffCRUD:
    async def get_all(
        self,
        db: AsyncSession,
        search: Optional[str] = None,
        sort_by: Optional[str] = "id",
        sort_order: Optional[str] = "asc",
    ):
        # Query User model and join with Staff to ensure we only get staff users
        query = (
            select(User)
            .options(
                selectinload(User.role),
                selectinload(User.branch_links).joinedload(UserBranch.branch),
                selectinload(User.staff),
            )
            .where(
                User.staff.has()  # Only users that have staff records
            )
        )

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.staff.has(
                        Staff.position.ilike(search_term)
                    ),  # Search in staff position
                )
            )

        # Define sortable columns - now using User fields directly
        sort_columns = {
            "id": User.id,
            "full_name": User.full_name,
            "email": User.email,
            "phone": User.phone,
            "position": Staff.position,  # This will work with the join
            "role_name": User.role_name,
            "status": User.status,
            "last_login": User.last_login,
            "created_at": User.created_at,
            "updated_at": User.updated_at,
        }

        # Get sort column with fallback to id
        safe_sort_by = sort_by or "id"
        sort_column = sort_columns.get(safe_sort_by, User.id)

        # Apply sorting
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        result = await sqlalchemy_paginate(db, query)
        return result

    async def get_by_id(self, db: AsyncSession, staff_id: int) -> Optional[Staff]:
        stmt = select(Staff).where(Staff.id == staff_id).options(joinedload(Staff.user))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def _sync_user_branches(
        self, db: AsyncSession, user: User, branch_ids: List[int]
    ):
        await db.execute(sa_delete(UserBranch).where(UserBranch.user_id == user.id))
        for bid in branch_ids:
            db.add(UserBranch(user_id=user.id, branch_id=bid))
        user.branch_id = branch_ids[0] if branch_ids else None
        db.add(user)
        await db.commit()
        await db.refresh(user)

    async def create(self, db: AsyncSession, data: dict) -> Staff:
        staff = Staff(**data)
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def update(self, db: AsyncSession, staff: Staff, data: dict) -> Staff:
        for field, value in data.items():
            setattr(staff, field, value)
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def delete(self, db: AsyncSession, staff: Staff) -> Staff:
        user = await db.get(User, staff.user_id)
        if user:
            user.status = UserStatus.deactive.value
            db.add(user)
            await db.commit()
        await db.refresh(staff)
        return staff

    async def approve(self, db: AsyncSession, staff: Staff) -> Staff:
        user = await db.get(User, staff.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")
        user.status = UserStatus.active.value
        db.add(user)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def reject(self, db: AsyncSession, staff: Staff) -> Staff:
        user = await db.get(User, staff.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Linked user not found")
        user.status = UserStatus.rejected.value
        db.add(user)
        await db.commit()
        await db.refresh(staff)
        return staff


staff_crud = StaffCRUD()
