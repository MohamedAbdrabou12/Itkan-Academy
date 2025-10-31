from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.staff.models import Staff
from app.modules.staff.schemas import StaffCreate, StaffUpdate


class StaffCRUD:
    async def get_all(self, db: AsyncSession) -> List[Staff]:
        result = await db.execute(Staff.__table__.select().order_by(Staff.id))
        return result.scalars().all()

    async def get_by_id(self, db: AsyncSession, staff_id: int) -> Optional[Staff]:
        result = await db.get(Staff, staff_id)
        return result

    async def create(self, db: AsyncSession, staff_in: StaffCreate) -> Staff:
        staff = Staff(**staff_in.dict())
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def update(
        self, db: AsyncSession, staff: Staff, staff_in: StaffUpdate
    ) -> Staff:
        for field, value in staff_in.dict(exclude_unset=True).items():
            setattr(staff, field, value)
        db.add(staff)
        await db.commit()
        await db.refresh(staff)
        return staff

    async def delete(self, db: AsyncSession, staff_id: int) -> None:
        staff = await self.get_by_id(db, staff_id)
        if staff:
            await db.delete(staff)
            await db.commit()


staff_crud = StaffCRUD()
