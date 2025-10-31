from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.modules.attendance.models import Attendance
from app.modules.attendance.schemas import AttendanceCreate, AttendanceUpdate


class AttendanceCRUD:
    async def get_all(self, db: AsyncSession) -> List[Attendance]:
        result = await db.execute(
            Attendance.__table__.select().order_by(Attendance.date)
        )
        return result.scalars().all()

    async def get_by_id(
        self, db: AsyncSession, attendance_id: int
    ) -> Optional[Attendance]:
        result = await db.get(Attendance, attendance_id)
        return result

    async def create(
        self, db: AsyncSession, attendance_in: AttendanceCreate
    ) -> Attendance:
        attendance = Attendance(**attendance_in.dict())
        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)
        return attendance

    async def update(
        self, db: AsyncSession, attendance: Attendance, attendance_in: AttendanceUpdate
    ) -> Attendance:
        for field, value in attendance_in.dict(exclude_unset=True).items():
            setattr(attendance, field, value)
        db.add(attendance)
        await db.commit()
        await db.refresh(attendance)
        return attendance

    async def delete(self, db: AsyncSession, attendance_id: int) -> None:
        attendance = await self.get_by_id(db, attendance_id)
        if attendance:
            await db.delete(attendance)
            await db.commit()


attendance_crud = AttendanceCRUD()
