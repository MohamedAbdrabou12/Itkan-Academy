from sqlalchemy import String, JSON, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, JSON, DateTime  # noqa
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.modules.users.models import User


class NotificationStatus(Enum):
    READ = "READ"
    UNREAD = "UNREAD"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(100))
    template: Mapped[str] = mapped_column(String(100))
    payload: Mapped[JSON] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(100))
    failed_message: Mapped[str] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="notifications", lazy="joined"
    )
