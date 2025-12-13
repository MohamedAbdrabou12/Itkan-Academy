from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declared_attr


class ReportType(Enum):
    ATTENDANCE = "attendance"
    EVALUATIONS = "evaluations"
    SUBSCRIPTIONS = "subscriptions"
    TEACHERS = "teachers"
    STAFF = "staff"
    FINANCE = "finance"


# class ReportStatus(Enum):
#     QUEUED = "queued"
#     APPROVED = "approved"
#     OVERDUE = "overdue"


class BaseReport(object):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    @declared_attr
    def created_by(cls):
        return relationship("User", lazy="joined")

    # status: Mapped[ReportStatus] = mapped_column(
    #     SQLEnum(ReportStatus), default=ReportStatus.QUEUED, nullable=False
    # )
