from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.attendance.models import (
    AttendanceLogType,
    AttendanceSourceType,
    AttendanceStatus,
    Weekday,
)


# Calendar Schemas
class CalendarWorkingDayBase(BaseModel):
    weekday: Weekday
    is_working: bool = True


class CalendarWorkingDayCreate(CalendarWorkingDayBase):
    pass


class CalendarWorkingDayRead(CalendarWorkingDayBase):
    id: int
    calendar_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CalendarHolidayBase(BaseModel):
    date: date
    name: str = Field(..., max_length=200)
    is_paid: bool = True


class CalendarHolidayCreate(CalendarHolidayBase):
    pass


class CalendarHolidayUpdate(BaseModel):
    date: Optional[date] = None
    name: Optional[str] = Field(None, max_length=200)
    is_paid: Optional[bool] = None


class CalendarHolidayRead(CalendarHolidayBase):
    id: int
    calendar_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SchoolCalendarBase(BaseModel):
    name: str = Field(..., max_length=100)
    timezone: str = Field(default="UTC", max_length=50)
    is_active: bool = True


class SchoolCalendarCreate(SchoolCalendarBase):
    branch_id: int
    working_days: Optional[List[CalendarWorkingDayCreate]] = None


class SchoolCalendarUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class SchoolCalendarRead(SchoolCalendarBase):
    id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime
    working_days: Optional[List[CalendarWorkingDayRead]] = None
    holidays: Optional[List[CalendarHolidayRead]] = None

    class Config:
        from_attributes = True


# Attendance Source Schemas
class AttendanceSourceBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: AttendanceSourceType


class AttendanceSourceCreate(AttendanceSourceBase):
    pass


class AttendanceSourceRead(AttendanceSourceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Work Schedule Schemas
class StaffWorkScheduleBase(BaseModel):
    start_time: time
    end_time: time
    grace_minutes: int = Field(default=15, ge=0, le=60)


class StaffWorkScheduleCreate(StaffWorkScheduleBase):
    user_id: int
    calendar_id: int


class StaffWorkScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    grace_minutes: Optional[int] = Field(None, ge=0, le=60)
    calendar_id: Optional[int] = None


class StaffWorkScheduleRead(StaffWorkScheduleBase):
    id: int
    user_id: int
    calendar_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Attendance Log Schemas
class AttendanceLogBase(BaseModel):
    timestamp: datetime
    type: AttendanceLogType
    source_id: Optional[int] = None
    device_id: Optional[str] = Field(None, max_length=100)


class AttendanceLogCreate(AttendanceLogBase):
    user_id: int
    branch_id: int


class AttendanceLogRead(AttendanceLogBase):
    id: int
    user_id: int
    branch_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Check-in/Check-out Schemas
class CheckInRequest(BaseModel):
    user_id: Optional[int] = None  # If None, use current user
    branch_id: Optional[int] = None  # If None, use current branch
    timestamp: Optional[datetime] = None  # If None, use current time
    source: AttendanceSourceType = AttendanceSourceType.manual
    device_id: Optional[str] = None


class CheckOutRequest(BaseModel):
    user_id: Optional[int] = None  # If None, use current user
    branch_id: Optional[int] = None  # If None, use current branch
    timestamp: Optional[datetime] = None  # If None, use current time
    source: AttendanceSourceType = AttendanceSourceType.manual
    device_id: Optional[str] = None


# Daily Attendance Summary Schemas
class AttendanceDailyBase(BaseModel):
    date: date
    status: AttendanceStatus
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    worked_minutes: Optional[int] = None
    remarks: Optional[str] = Field(None, max_length=500)


class AttendanceDailyCreate(AttendanceDailyBase):
    user_id: int
    branch_id: int


class AttendanceDailyUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    check_in_time: Optional[time] = None
    check_out_time: Optional[time] = None
    worked_minutes: Optional[int] = None
    remarks: Optional[str] = Field(None, max_length=500)


class AttendanceDailyRead(AttendanceDailyBase):
    id: int
    user_id: int
    branch_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Response Schemas
class CheckInResponse(BaseModel):
    success: bool
    message: str
    attendance_log: Optional[AttendanceLogRead] = None
    is_late: Optional[bool] = None


class CheckOutResponse(BaseModel):
    success: bool
    message: str
    attendance_log: Optional[AttendanceLogRead] = None
    daily_summary: Optional[AttendanceDailyRead] = None
