# backend/app/modules/staff/models.py
from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List  # noqa
from sqlalchemy import ForeignKey, String, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.models import User


class Staff(Base):
    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    position: Mapped[Optional[str]] = mapped_column(String(100))
    salary_meta: Mapped[Optional[dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="staff", lazy="joined"
    )

    def __repr__(self):
        return f"<Staff(id={self.id}, user={getattr(self.user, 'full_name', None)})>"
