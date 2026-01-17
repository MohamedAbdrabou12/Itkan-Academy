from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.crud import (
    attendance_daily_crud,
    attendance_log_crud,
    attendance_source_crud,
    calendar_crud,
    calendar_holiday_crud,
    calendar_working_day_crud,
    staff_work_schedule_crud,
)
from app.modules.attendance.models import (
    AttendanceDaily,
    AttendanceLog,
    AttendanceLogType,
    AttendanceSourceType,
    AttendanceStatus,
    Weekday,
)
from app.modules.attendance.schemas import (
    AttendanceDailyRead,
    AttendanceLogRead,
    CheckInResponse,
    CheckOutResponse,
)
from app.modules.branches.models import Branch
from app.modules.users.models import User


class AttendanceService:
    @staticmethod
    def _get_weekday(date_obj: date) -> Weekday:
        """Convert Python weekday (0=Monday) to our Weekday enum."""
        weekday_map = {
            0: Weekday.mon,
            1: Weekday.tue,
            2: Weekday.wed,
            3: Weekday.thu,
            4: Weekday.fri,
            5: Weekday.sat,
            6: Weekday.sun,
        }
        return weekday_map[date_obj.weekday()]

    @staticmethod
    async def _get_active_calendar(
        db: AsyncSession, branch_id: int
    ) -> Optional[object]:
        """Get the active calendar for a branch."""
        calendars = await calendar_crud.get_by_branch_id(db, branch_id, is_active=True)
        return calendars[0] if calendars else None

    @staticmethod
    async def _is_working_day(
        db: AsyncSession, calendar_id: int, check_date: date
    ) -> bool:
        """Check if a date is a working day."""
        # Check if it's a holiday
        is_holiday = await calendar_holiday_crud.is_holiday(
            db, calendar_id, check_date
        )
        if is_holiday:
            return False

        # Check weekday configuration
        weekday = AttendanceService._get_weekday(check_date)
        working_days = await calendar_working_day_crud.get_by_calendar_id(
            db, calendar_id
        )
        for wd in working_days:
            if wd.weekday == weekday:
                return wd.is_working
        return False  # Default to non-working if not configured

    @staticmethod
    async def _get_user_schedule(
        db: AsyncSession, user_id: int, branch_id: int
    ) -> Optional[object]:
        """Get user's work schedule for a branch."""
        calendar = await AttendanceService._get_active_calendar(db, branch_id)
        if not calendar:
            return None

        schedule = await staff_work_schedule_crud.get_by_user_id(
            db, user_id, calendar.id
        )
        return schedule

    @staticmethod
    async def check_in(
        db: AsyncSession,
        user_id: int,
        branch_id: int,
        timestamp: Optional[datetime] = None,
        source_type: AttendanceSourceType = AttendanceSourceType.manual,
        device_id: Optional[str] = None,
    ) -> CheckInResponse:
        """Record a check-in event."""
        if timestamp is None:
            timestamp = datetime.utcnow()

        check_date = timestamp.date()

        # Get or create attendance source
        source = await attendance_source_crud.get_or_create_by_type(
            db, source_type.value, source_type.value.title()
        )

        # Check if already checked in today
        existing_logs = await attendance_log_crud.get_by_user_and_date(
            db, user_id, branch_id, check_date, "check_in"
        )
        if existing_logs:
            latest = existing_logs[-1]
            return CheckInResponse(
                success=False,
                message="Already checked in today",
                attendance_log=AttendanceLogRead.from_orm(latest),
                is_late=False,
            )

        # Create attendance log
        log_data = {
            "user_id": user_id,
            "branch_id": branch_id,
            "timestamp": timestamp,
            "type": AttendanceLogType.check_in.value,
            "source_id": source.id,
            "device_id": device_id,
        }
        log = await attendance_log_crud.create(db, log_data)

        # Check if late
        is_late = False
        schedule = await AttendanceService._get_user_schedule(db, user_id, branch_id)
        if schedule:
            check_in_time = timestamp.time()
            grace_time = timedelta(minutes=schedule.grace_minutes)
            expected_time = datetime.combine(check_date, schedule.start_time)
            late_threshold = expected_time + grace_time

            if timestamp > late_threshold:
                is_late = True

        # Calculate daily attendance (will be recalculated at end of day or checkout)
        await AttendanceService._calculate_daily_attendance(
            db, user_id, branch_id, check_date
        )

        return CheckInResponse(
            success=True,
            message="Checked in successfully",
            attendance_log=AttendanceLogRead.from_orm(log),
            is_late=is_late,
        )

    @staticmethod
    async def check_out(
        db: AsyncSession,
        user_id: int,
        branch_id: int,
        timestamp: Optional[datetime] = None,
        source_type: AttendanceSourceType = AttendanceSourceType.manual,
        device_id: Optional[str] = None,
    ) -> CheckOutResponse:
        """Record a check-out event."""
        if timestamp is None:
            timestamp = datetime.utcnow()

        check_date = timestamp.date()

        # Verify check-in exists
        check_in_log = await attendance_log_crud.get_latest_check_in(
            db, user_id, branch_id, check_date
        )
        if not check_in_log:
            raise HTTPException(
                status_code=400, detail="Cannot check out without checking in first"
            )

        # Get or create attendance source
        source = await attendance_source_crud.get_or_create_by_type(
            db, source_type.value, source_type.value.title()
        )

        # Create attendance log
        log_data = {
            "user_id": user_id,
            "branch_id": branch_id,
            "timestamp": timestamp,
            "type": AttendanceLogType.check_out.value,
            "source_id": source.id,
            "device_id": device_id,
        }
        log = await attendance_log_crud.create(db, log_data)

        # Calculate daily attendance
        daily = await AttendanceService._calculate_daily_attendance(
            db, user_id, branch_id, check_date
        )

        return CheckOutResponse(
            success=True,
            message="Checked out successfully",
            attendance_log=AttendanceLogRead.from_orm(log),
            daily_summary=AttendanceDailyRead.from_orm(daily) if daily else None,
        )

    @staticmethod
    async def _calculate_daily_attendance(
        db: AsyncSession, user_id: int, branch_id: int, check_date: date
    ) -> Optional[AttendanceDaily]:
        """Calculate and update daily attendance summary."""
        # Get calendar and check if working day
        calendar = await AttendanceService._get_active_calendar(db, branch_id)
        if not calendar:
            # No calendar configured, mark as absent
            status = AttendanceStatus.absent
        else:
            is_working = await AttendanceService._is_working_day(
                db, calendar.id, check_date
            )
            if not is_working:
                status = AttendanceStatus.on_leave
            else:
                # Check for check-in/check-out logs
                check_in = await attendance_log_crud.get_latest_check_in(
                    db, user_id, branch_id, check_date
                )
                check_out = await attendance_log_crud.get_latest_check_out(
                    db, user_id, branch_id, check_date
                )

                if not check_in:
                    status = AttendanceStatus.absent
                else:
                    check_in_time = check_in.timestamp.time()
                    check_out_time = check_out.timestamp.time() if check_out else None

                    # Get user schedule
                    schedule = await AttendanceService._get_user_schedule(
                        db, user_id, branch_id
                    )

                    if schedule:
                        # Check if late
                        grace_time = timedelta(minutes=schedule.grace_minutes)
                        expected_start = datetime.combine(
                            check_date, schedule.start_time
                        )
                        late_threshold = expected_start + grace_time
                        check_in_datetime = datetime.combine(check_date, check_in_time)

                        if check_in_datetime > late_threshold:
                            status = AttendanceStatus.late
                        else:
                            # Check if half day
                            if check_out_time:
                                check_in_dt = datetime.combine(check_date, check_in_time)
                                check_out_dt = datetime.combine(
                                    check_date, check_out_time
                                )
                                worked_minutes = (
                                    check_out_dt - check_in_dt
                                ).total_seconds() / 60

                                # Consider half day if worked less than 4 hours
                                if worked_minutes < 240:
                                    status = AttendanceStatus.half_day
                                else:
                                    status = AttendanceStatus.present
                            else:
                                # No check-out yet, assume present for now
                                status = AttendanceStatus.present
                    else:
                        # No schedule, just mark as present if checked in
                        status = AttendanceStatus.present

        # Get or create daily attendance record
        daily = await attendance_daily_crud.get_by_user_and_date(
            db, user_id, branch_id, check_date
        )

        # Get check-in/check-out times
        check_in = await attendance_log_crud.get_latest_check_in(
            db, user_id, branch_id, check_date
        )
        check_out = await attendance_log_crud.get_latest_check_out(
            db, user_id, branch_id, check_date
        )

        check_in_time = check_in.timestamp.time() if check_in else None
        check_out_time = check_out.timestamp.time() if check_out else None

        # Calculate worked minutes
        worked_minutes = None
        if check_in_time and check_out_time:
            check_in_dt = datetime.combine(check_date, check_in_time)
            check_out_dt = datetime.combine(check_date, check_out_time)
            worked_minutes = int((check_out_dt - check_in_dt).total_seconds() / 60)

        daily_data = {
            "user_id": user_id,
            "branch_id": branch_id,
            "date": check_date,
            "status": status.value,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
            "worked_minutes": worked_minutes,
        }

        if daily:
            daily = await attendance_daily_crud.update(db, daily, daily_data)
        else:
            daily = await attendance_daily_crud.create(db, daily_data)

        return daily

    @staticmethod
    async def get_daily_attendance(
        db: AsyncSession,
        user_id: Optional[int] = None,
        branch_id: Optional[int] = None,
        check_date: Optional[date] = None,
    ) -> List[Dict]:
        """Get daily attendance records."""
        if check_date is None:
            check_date = date.today()

        if user_id:
            if branch_id:
                daily = await attendance_daily_crud.get_by_user_and_date(
                    db, user_id, branch_id, check_date
                )
                if daily:
                    return [AttendanceDailyRead.from_orm(daily).dict()]
                return []
            else:
                # Get all branches for user
                from_date = check_date
                to_date = check_date
                records = await attendance_daily_crud.get_by_user_date_range(
                    db, user_id, None, from_date, to_date
                )
                return [AttendanceDailyRead.from_orm(r).dict() for r in records]
        else:
            # Get all records for date
            records = await attendance_daily_crud.get_by_date(db, check_date, branch_id)
            return [AttendanceDailyRead.from_orm(r).dict() for r in records]

    @staticmethod
    async def get_user_attendance_range(
        db: AsyncSession,
        user_id: int,
        branch_id: Optional[int],
        from_date: date,
        to_date: date,
    ) -> List[Dict]:
        """Get attendance records for a user in a date range."""
        records = await attendance_daily_crud.get_by_user_date_range(
            db, user_id, branch_id, from_date, to_date
        )
        return [AttendanceDailyRead.from_orm(r).dict() for r in records]
