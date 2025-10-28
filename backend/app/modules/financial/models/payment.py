from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# Avoid circular imports
if TYPE_CHECKING:
    from app.modules.financial.models.invoice import Invoice


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )
    external_txn_id: Mapped[Optional[str]] = mapped_column(String(100))
    gateway: Mapped[Optional[str]] = mapped_column(String(50))
    amount: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    inf_metadata: Mapped[Optional[Dict]] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    invoice: Mapped[Invoice] = relationship(
        "Invoice", back_populates="payments", lazy="selectin"
    )
