from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

from sqlalchemy import String, JSON, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.users.models import User


class ReportJob(Base):
    __tablename__ = "reports_jobs"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Report job details
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    params: Mapped[Optional[Dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)
    result_url: Mapped[Optional[str]] = mapped_column(Text)

    # Foreign keys
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    # Timestamp fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    created_user: Mapped[Optional[User]] = relationship("User", lazy="joined")
