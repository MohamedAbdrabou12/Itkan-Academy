from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

import sqlalchemy
from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.users.models import User


class PayrollCycleStatus(Enum):
    DRAFT = "draft"
    LOCKED = "locked"
    APPROVED = "approved"
    PAID = "paid"


class PayrollCycle(Base):
    __tablename__ = "payroll_cycles"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[int] = mapped_column(nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[PayrollCycleStatus] = mapped_column(
        sqlalchemy.Enum(PayrollCycleStatus), nullable=False, default=PayrollCycleStatus.DRAFT
    )

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    approved_by: Mapped["User | None"] = relationship(
        "User", foreign_keys=[approved_by_id], lazy="selectin"
    )
