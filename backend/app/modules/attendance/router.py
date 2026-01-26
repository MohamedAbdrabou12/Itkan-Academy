from datetime import date as dt_date, datetime
from typing import List, Optional

from app.core.auth import get_current_user
from app.core.authorization import require_permission
from app.db.session import get_db
from app.modules.attendance.schemas import (
    AttendanceSourceCreate,
    AttendanceSourceRead,
    CalendarHolidayCreate,
    CalendarHolidayRead,
    CalendarHolidayUpdate,
    CalendarWorkingDayCreate,
    CalendarWorkingDayRead,
    CheckInRequest,
    CheckInResponse,
    CheckOutRequest,
    CheckOutResponse,
    SchoolCalendarCreate,
    SchoolCalendarRead,
    SchoolCalendarUpdate,
    StaffWorkScheduleCreate,
    StaffWorkScheduleRead,
    StaffWorkScheduleReadWithDetails,
    StaffWorkScheduleUpdate,
)
from app.modules.attendance.service import attendance_service
from app.modules.permissions.permissions import PermissionCode
from app.modules.users.models import User
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

attendance_router = APIRouter(prefix="/attendance", tags=["Attendance"])


# ========== Calendar Management ==========


# revied
@attendance_router.post(
    "/calendars",
    response_model=SchoolCalendarRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def create_calendar(
    calendar_in: SchoolCalendarCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new school calendar."""
    return await attendance_service.create_calendar(db, calendar_in, user)


# revied
@attendance_router.get(
    "/calendars",
    response_model=List[SchoolCalendarRead],
)
async def list_calendars(
    branch_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List school calendars."""
    return await attendance_service.list_calendars(db, branch_id, is_active)


# revied
@attendance_router.put(
    "/calendars/{calendar_id}",
    response_model=SchoolCalendarRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def update_calendar(
    calendar_id: int,
    calendar_in: SchoolCalendarUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a school calendar."""
    return await attendance_service.update_calendar(db, calendar_id, calendar_in)


# revied
@attendance_router.delete(
    "/calendars/{calendar_id}",
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def delete_calendar(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a school calendar."""
    return await attendance_service.delete_calendar(db, calendar_id)


# revied
@attendance_router.get(
    "/calendars/{calendar_id}/working-days",
    response_model=List[CalendarWorkingDayRead],
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def get_working_days(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get working days for a calendar."""
    return await attendance_service.get_working_days(db, calendar_id)


# revied
@attendance_router.post(
    "/calendars/{calendar_id}/working-days",
    response_model=List[CalendarWorkingDayRead],
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def set_working_days(
    calendar_id: int,
    working_days: List[CalendarWorkingDayCreate],
    db: AsyncSession = Depends(get_db),
):
    """Set working days for a calendar."""
    return await attendance_service.set_working_days(db, calendar_id, working_days)


# revied
@attendance_router.post(
    "/calendars/{calendar_id}/holidays",
    response_model=CalendarHolidayRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def create_holiday(
    calendar_id: int,
    holiday_in: CalendarHolidayCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a holiday for a calendar."""
    return await attendance_service.create_holiday(db, calendar_id, holiday_in)


# revied
@attendance_router.put(
    "/calendars/{calendar_id}/holidays/{holiday_id}",
    response_model=CalendarHolidayRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def update_holiday(
    calendar_id: int,
    holiday_id: int,
    holiday_in: CalendarHolidayUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a holiday for a calendar."""
    return await attendance_service.update_holiday(
        db, calendar_id, holiday_id, holiday_in
    )


# revied
@attendance_router.delete(
    "/calendars/{calendar_id}/holidays/{holiday_id}",
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def delete_holiday(
    calendar_id: int,
    holiday_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a holiday for a calendar."""
    return await attendance_service.delete_holiday(db, calendar_id, holiday_id)


# revied
@attendance_router.get(
    "/calendars/{calendar_id}/holidays",
    response_model=List[CalendarHolidayRead],
)
async def list_holidays(
    calendar_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List holidays for a calendar."""
    return await attendance_service.list_holidays(db, calendar_id)


# ========== Work Schedule Management ==========
@attendance_router.post(
    "/work-schedules",
    response_model=StaffWorkScheduleRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def create_work_schedule(
    schedule_in: StaffWorkScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a work schedule for a user."""
    return await attendance_service.create_work_schedule(db, schedule_in)


@attendance_router.get(
    "/work-schedules",
    response_model=list[StaffWorkScheduleReadWithDetails],
    dependencies=[Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_VIEW))],
)
async def list_work_schedules(
    user_id: Optional[int] = Query(None),
    calendar_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List work schedules."""
    return await attendance_service.list_work_schedules(db, user_id, calendar_id)


@attendance_router.put(
    "/work-schedules/{schedule_id}",
    response_model=StaffWorkScheduleRead,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def update_work_schedule(
    schedule_id: int,
    schedule_in: StaffWorkScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a work schedule."""
    return await attendance_service.update_work_schedule(db, schedule_id, schedule_in)


@attendance_router.delete(
    "/work-schedules/{schedule_id}",
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def delete_work_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a work schedule."""
    return await attendance_service.delete_work_schedule(db, schedule_id)


# ========== Attendance Logging ==========
@attendance_router.post(
    "/check-in",
    response_model=CheckInResponse,
    dependencies=[Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CHECKIN))],
)
async def check_in(
    request: CheckInRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check in for attendance."""
    user_id = request.user_id or current_user.id
    branch_id = request.branch_id
    if not branch_id:
        branch_id = getattr(req.state, "active_branch_id", None)
    if not branch_id:
        raise HTTPException(status_code=400, detail="لم يتم تحديد الفرع")

    timestamp = request.timestamp or datetime.utcnow()

    return await attendance_service.check_in(
        db,
        user_id=user_id,
        branch_id=branch_id,
        timestamp=timestamp,
        source_type=request.source,
        device_id=request.device_id,
    )


@attendance_router.post(
    "/check-out",
    dependencies=[Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CHECKIN))],
)
async def check_out(
    request: CheckOutRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check out from attendance."""
    user_id = request.user_id or current_user.id
    branch_id = request.branch_id
    if not branch_id:
        branch_id = getattr(req.state, "active_branch_id", None)
    if not branch_id:
        raise HTTPException(status_code=400, detail="Branch ID is required")

    timestamp = request.timestamp or datetime.utcnow()

    return await attendance_service.check_out(
        db,
        user_id=user_id,
        branch_id=branch_id,
        timestamp=timestamp,
        source_type=request.source,
        device_id=request.device_id,
    )


# ========== Daily Summary & Reports ==========
@attendance_router.get(
    "/daily",
    dependencies=[Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_VIEW))],
)
async def get_daily_attendance(
    date: Optional[dt_date] = Query(None, description="Date (default: today)"),
    user_id: Optional[int] = Query(None),
    branch_id: Optional[int] = Query(None),
    req: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get daily attendance records."""
    if not branch_id:
        branch_id = getattr(req.state, "active_branch_id", None) if req else None

    records = await attendance_service.get_daily_attendance(
        db, user_id=user_id, branch_id=branch_id, check_date=date
    )
    return records


@attendance_router.get(
    "/user/{user_id}",
    dependencies=[Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_VIEW))],
)
async def get_user_attendance(
    user_id: int,
    from_date: dt_date = Query(..., description="Start date"),
    to_date: dt_date = Query(..., description="End date"),
    branch_id: Optional[int] = Query(None),
    req: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Get attendance records for a user in a date range."""
    if not branch_id:
        branch_id = getattr(req.state, "active_branch_id", None) if req else None

    records = await attendance_service.get_user_attendance_range(
        db, user_id, branch_id, from_date, to_date
    )
    return records


# ========== Attendance Sources ==========
@attendance_router.post(
    "/sources",
    response_model=AttendanceSourceRead,
    status_code=201,
    dependencies=[
        Depends(require_permission(PermissionCode.STAFF_ATTENDANCE_CALENDAR_MANAGE))
    ],
)
async def create_attendance_source(
    source_in: AttendanceSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create an attendance source."""
    return await attendance_service.create_attendance_source(db, source_in)
