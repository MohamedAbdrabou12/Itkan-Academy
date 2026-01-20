from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.attendance.models import (
    AttendanceDaily,
    AttendanceLog,
    AttendanceSource,
    CalendarHoliday,
    CalendarWorkingDay,
    SchoolCalendar,
    StaffWorkSchedule,
)
from app.modules.users.models import User


class CalendarCRUD:
    async def create(self, db: AsyncSession, calendar_data: dict) -> SchoolCalendar:
        calendar = SchoolCalendar(**calendar_data)
        db.add(calendar)
        await db.commit()
        await db.refresh(calendar)
        return calendar

    async def get_by_id(
        self, db: AsyncSession, calendar_id: int
    ) -> Optional[SchoolCalendar]:
        stmt = (
            select(SchoolCalendar)
            .where(SchoolCalendar.id == calendar_id)
            .options(
                selectinload(SchoolCalendar.working_days),
                selectinload(SchoolCalendar.holidays),
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_branch_id(
        self, db: AsyncSession, branch_id: int, is_active: Optional[bool] = None
    ) -> List[SchoolCalendar]:
        stmt = select(SchoolCalendar).where(SchoolCalendar.branch_id == branch_id)
        if is_active is not None:
            stmt = stmt.where(SchoolCalendar.is_active == is_active)
        stmt = stmt.options(
            selectinload(SchoolCalendar.working_days),
            selectinload(SchoolCalendar.holidays),
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, calendar: SchoolCalendar, data: dict
    ) -> SchoolCalendar:
        for field, value in data.items():
            setattr(calendar, field, value)
        db.add(calendar)
        await db.commit()
        await db.refresh(calendar)
        return calendar

    async def delete(self, db: AsyncSession, calendar_id: int) -> bool:
        calendar = await self.get_by_id(db, calendar_id)
        if calendar:
            await db.delete(calendar)
            await db.commit()
            return True
        return False


class CalendarWorkingDayCRUD:
    async def create(
        self, db: AsyncSession, working_day_data: dict
    ) -> CalendarWorkingDay:
        working_day = CalendarWorkingDay(**working_day_data)
        db.add(working_day)
        await db.commit()
        await db.refresh(working_day)
        return working_day

    async def create_bulk(
        self, db: AsyncSession, calendar_id: int, working_days: List[dict]
    ) -> List[CalendarWorkingDay]:
        # Delete existing working days for this calendar
        old_working_days = await self.get_by_calendar_id(db, calendar_id)
        for wd in old_working_days:
            await db.delete(wd)
        await db.commit()

        # Create new working days
        result = await db.execute(
            select(CalendarWorkingDay).where(
                CalendarWorkingDay.calendar_id == calendar_id
            )
        )
        existing = result.scalars().all()
        for wd in existing:
            await db.delete(wd)

        # Create new working days
        new_working_days = [
            CalendarWorkingDay(calendar_id=calendar_id, **wd) for wd in working_days
        ]
        db.add_all(new_working_days)
        await db.commit()
        for wd in new_working_days:
            await db.refresh(wd)
        return new_working_days

    async def get_by_calendar_id(
        self, db: AsyncSession, calendar_id: int
    ) -> List[CalendarWorkingDay]:
        stmt = select(CalendarWorkingDay).where(
            CalendarWorkingDay.calendar_id == calendar_id
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class CalendarHolidayCRUD:
    async def create(self, db: AsyncSession, holiday_data: dict) -> CalendarHoliday:
        holiday = CalendarHoliday(**holiday_data)
        db.add(holiday)
        await db.commit()
        await db.refresh(holiday)
        return holiday

    async def get_by_calendar_id(
        self, db: AsyncSession, calendar_id: int, holiday_date: Optional[date] = None
    ) -> List[CalendarHoliday]:
        stmt = select(CalendarHoliday).where(CalendarHoliday.calendar_id == calendar_id)
        if holiday_date:
            stmt = stmt.where(CalendarHoliday.date == holiday_date)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def is_holiday(
        self, db: AsyncSession, calendar_id: int, check_date: date
    ) -> bool:
        stmt = select(CalendarHoliday).where(
            and_(
                CalendarHoliday.calendar_id == calendar_id,
                CalendarHoliday.date == check_date,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def update(
        self, db: AsyncSession, holiday: CalendarHoliday, data: dict
    ) -> CalendarHoliday:
        for field, value in data.items():
            setattr(holiday, field, value)
        db.add(holiday)
        await db.commit()
        await db.refresh(holiday)
        return holiday

    async def delete(self, db: AsyncSession, holiday_id: int) -> bool:
        stmt = select(CalendarHoliday).where(CalendarHoliday.id == holiday_id)
        result = await db.execute(stmt)
        holiday = result.scalar_one_or_none()
        if holiday:
            await db.delete(holiday)
            await db.commit()
            return True
        return False


class AttendanceSourceCRUD:
    async def create(self, db: AsyncSession, source_data: dict) -> AttendanceSource:
        source = AttendanceSource(**source_data)
        db.add(source)
        await db.commit()
        await db.refresh(source)
        return source

    async def get_by_id(
        self, db: AsyncSession, source_id: int
    ) -> Optional[AttendanceSource]:
        stmt = select(AttendanceSource).where(AttendanceSource.id == source_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_type(
        self, db: AsyncSession, source_type: str
    ) -> Optional[AttendanceSource]:
        stmt = select(AttendanceSource).where(AttendanceSource.type == source_type)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create_by_type(
        self, db: AsyncSession, source_type: str, name: Optional[str] = None
    ) -> AttendanceSource:
        source = await self.get_by_type(db, source_type)
        if not source:
            source = await self.create(
                db, {"name": name or source_type.title(), "type": source_type}
            )
        return source


class StaffWorkScheduleCRUD:
    async def create(self, db: AsyncSession, schedule_data: dict) -> StaffWorkSchedule:
        schedule = StaffWorkSchedule(**schedule_data)
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    async def get_by_id(
        self, db: AsyncSession, schedule_id: int
    ) -> Optional[StaffWorkSchedule]:
        stmt = select(StaffWorkSchedule).where(StaffWorkSchedule.id == schedule_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, db: AsyncSession, user_id: int, calendar_id: Optional[int] = None
    ) -> Optional[StaffWorkSchedule]:
        stmt = select(StaffWorkSchedule).where(StaffWorkSchedule.user_id == user_id)
        if calendar_id:
            stmt = stmt.where(StaffWorkSchedule.calendar_id == calendar_id)
        stmt = stmt.options(joinedload(StaffWorkSchedule.calendar))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        calendar_id: Optional[int] = None,
    ) -> List[StaffWorkSchedule]:
        stmt = select(StaffWorkSchedule)
        if user_id:
            stmt = stmt.where(StaffWorkSchedule.user_id == user_id)
        if calendar_id:
            stmt = stmt.where(StaffWorkSchedule.calendar_id == calendar_id)
        stmt = stmt.options(
            joinedload(StaffWorkSchedule.calendar).selectinload(
                SchoolCalendar.working_days
            ),
            joinedload(StaffWorkSchedule.calendar).selectinload(
                SchoolCalendar.holidays
            ),
            joinedload(StaffWorkSchedule.user).joinedload(User.role),
            joinedload(StaffWorkSchedule.user).selectinload(User.branches),
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, schedule: StaffWorkSchedule, data: dict
    ) -> StaffWorkSchedule:
        for field, value in data.items():
            setattr(schedule, field, value)
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)
        return schedule

    async def delete(self, db: AsyncSession, schedule_id: int) -> bool:
        stmt = select(StaffWorkSchedule).where(StaffWorkSchedule.id == schedule_id)
        result = await db.execute(stmt)
        schedule = result.scalar_one_or_none()
        if schedule:
            await db.delete(schedule)
            await db.commit()
            return True
        return False


class AttendanceLogCRUD:
    async def create(self, db: AsyncSession, log_data: dict) -> AttendanceLog:
        log = AttendanceLog(**log_data)
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    async def get_by_user_and_date(
        self,
        db: AsyncSession,
        user_id: int,
        branch_id: int,
        check_date: date,
        log_type: Optional[str] = None,
    ) -> List[AttendanceLog]:
        start_datetime = datetime.combine(check_date, time.min)
        end_datetime = datetime.combine(check_date, time.max)

        stmt = select(AttendanceLog).where(
            and_(
                AttendanceLog.user_id == user_id,
                AttendanceLog.branch_id == branch_id,
                AttendanceLog.timestamp >= start_datetime,
                AttendanceLog.timestamp <= end_datetime,
            )
        )
        if log_type:
            stmt = stmt.where(AttendanceLog.type == log_type)
        stmt = stmt.order_by(AttendanceLog.timestamp)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_check_in(
        self, db: AsyncSession, user_id: int, branch_id: int, check_date: date
    ) -> Optional[AttendanceLog]:
        logs = await self.get_by_user_and_date(
            db, user_id, branch_id, check_date, "check_in"
        )
        return logs[-1] if logs else None

    async def get_latest_check_out(
        self, db: AsyncSession, user_id: int, branch_id: int, check_date: date
    ) -> Optional[AttendanceLog]:
        logs = await self.get_by_user_and_date(
            db, user_id, branch_id, check_date, "check_out"
        )
        return logs[-1] if logs else None


class AttendanceDailyCRUD:
    async def create(self, db: AsyncSession, daily_data: dict) -> AttendanceDaily:
        daily = AttendanceDaily(**daily_data)
        db.add(daily)
        await db.commit()
        await db.refresh(daily)
        return daily

    async def get_by_user_and_date(
        self,
        db: AsyncSession,
        user_id: int,
        branch_id: int,
        check_date: date,
    ) -> Optional[AttendanceDaily]:
        stmt = select(AttendanceDaily).where(
            and_(
                AttendanceDaily.user_id == user_id,
                AttendanceDaily.branch_id == branch_id,
                AttendanceDaily.date == check_date,
            )
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_date_range(
        self,
        db: AsyncSession,
        user_id: int,
        branch_id: Optional[int],
        from_date: date,
        to_date: date,
    ) -> List[AttendanceDaily]:
        stmt = select(AttendanceDaily).where(
            and_(
                AttendanceDaily.user_id == user_id,
                AttendanceDaily.date >= from_date,
                AttendanceDaily.date <= to_date,
            )
        )
        if branch_id:
            stmt = stmt.where(AttendanceDaily.branch_id == branch_id)
        stmt = stmt.order_by(AttendanceDaily.date)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, db: AsyncSession, daily: AttendanceDaily, data: dict
    ) -> AttendanceDaily:
        for field, value in data.items():
            setattr(daily, field, value)
        db.add(daily)
        await db.commit()
        await db.refresh(daily)
        return daily

    async def get_by_date(
        self, db: AsyncSession, check_date: date, branch_id: Optional[int] = None
    ) -> List[AttendanceDaily]:
        stmt = select(AttendanceDaily).where(AttendanceDaily.date == check_date)
        if branch_id:
            stmt = stmt.where(AttendanceDaily.branch_id == branch_id)
        stmt = stmt.options(joinedload(AttendanceDaily.user))
        result = await db.execute(stmt)
        return list(result.scalars().all())


# Singleton instances
calendar_crud = CalendarCRUD()
calendar_working_day_crud = CalendarWorkingDayCRUD()
calendar_holiday_crud = CalendarHolidayCRUD()
attendance_source_crud = AttendanceSourceCRUD()
staff_work_schedule_crud = StaffWorkScheduleCRUD()
attendance_log_crud = AttendanceLogCRUD()
attendance_daily_crud = AttendanceDailyCRUD()
