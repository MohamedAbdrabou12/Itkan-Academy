from __future__ import annotations
from datetime import date, datetime, time
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.users.models import User


class Weekday(str, Enum):
    mon = "mon"
    tue = "tue"
    wed = "wed"
    thu = "thu"
    fri = "fri"
    sat = "sat"
    sun = "sun"


class AttendanceSourceType(str, Enum):
    manual = "manual"
    biometric = "biometric"
    rfid = "rfid"
    mobile = "mobile"
    api = "api"


class AttendanceLogType(str, Enum):
    check_in = "check_in"
    check_out = "check_out"


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    late = "late"
    half_day = "half_day"
    on_leave = "on_leave"


class SchoolCalendar(Base):
    __tablename__ = "school_calendars"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    branch: Mapped["Branch"] = relationship("Branch", back_populates="calendars")
    working_days: Mapped[List["CalendarWorkingDay"]] = relationship(
        "CalendarWorkingDay",
        back_populates="calendar",
        cascade="all, delete-orphan",
    )
    holidays: Mapped[List["CalendarHoliday"]] = relationship(
        "CalendarHoliday",
        back_populates="calendar",
        cascade="all, delete-orphan",
    )
    work_schedules: Mapped[List["StaffWorkSchedule"]] = relationship(
        "StaffWorkSchedule", back_populates="calendar"
    )


class CalendarWorkingDay(Base):
    __tablename__ = "calendar_working_days"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("school_calendars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    weekday: Mapped[Weekday] = mapped_column(String(10), nullable=False)
    is_working: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    calendar: Mapped["SchoolCalendar"] = relationship(
        "SchoolCalendar", back_populates="working_days"
    )

    __table_args__ = (
        UniqueConstraint("calendar_id", "weekday", name="uq_calendar_weekday"),
    )


class CalendarHoliday(Base):
    __tablename__ = "calendar_holidays"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("school_calendars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    calendar: Mapped["SchoolCalendar"] = relationship(
        "SchoolCalendar", back_populates="holidays"
    )

    __table_args__ = (
        UniqueConstraint("calendar_id", "date", name="uq_calendar_holiday_date"),
    )


class AttendanceSource(Base):
    __tablename__ = "attendance_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[AttendanceSourceType] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    attendance_logs: Mapped[List["AttendanceLog"]] = relationship(
        "AttendanceLog", back_populates="source"
    )


class StaffWorkSchedule(Base):
    __tablename__ = "staff_work_schedules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    calendar_id: Mapped[int] = mapped_column(
        ForeignKey("school_calendars.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    grace_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="work_schedules")
    calendar: Mapped["SchoolCalendar"] = relationship(
        "SchoolCalendar", back_populates="work_schedules"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "calendar_id", name="uq_user_calendar"),
    )


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    type: Mapped[AttendanceLogType] = mapped_column(String(20), nullable=False)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("attendance_sources.id", ondelete="SET NULL"), nullable=True
    )
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attendance_logs")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="attendance_logs")
    source: Mapped[Optional["AttendanceSource"]] = relationship(
        "AttendanceSource", back_populates="attendance_logs"
    )


class AttendanceDaily(Base):
    __tablename__ = "attendance_daily"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    branch_id: Mapped[int] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(String(20), nullable=False)
    check_in_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    check_out_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    worked_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attendance_daily")
    branch: Mapped["Branch"] = relationship("Branch", back_populates="attendance_daily")

    __table_args__ = (
        UniqueConstraint("user_id", "branch_id", "date", name="uq_user_branch_date"),
    )
