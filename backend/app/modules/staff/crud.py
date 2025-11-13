# backend/app/modules/staff/crud.py
from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy import delete as sa_delete
from app.modules.staff.models import Staff
from app.modules.users.models import User, UserBranch, UserStatus


class StaffCRUD:
    async def get_all(self, db: AsyncSession):
        stmt = select(Staff).options(joinedload(Staff.user)).order_by(Staff.id)
        result = await db.execute(stmt)
        return result.scalars().all()

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
