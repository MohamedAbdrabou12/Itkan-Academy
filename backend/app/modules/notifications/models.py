# app/modules/notifications/models.py
from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.models import User


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    template: Mapped[Optional[str]] = mapped_column(String(100))
    payload: Mapped[Optional[Dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    user: Mapped[User] = relationship(
        "User", back_populates="notifications", lazy="selectin"
    )
