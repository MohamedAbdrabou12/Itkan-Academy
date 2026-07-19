import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, final

from app.db.base import Base
from sqlalchemy import VARCHAR, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.branches.models import Branch
    from app.modules.curriculums.models.curriculum import Curriculum
    from app.modules.enrolments.models.enrolment import Enrolment


@final
class EnrolmentPricingPlan(Base):
    __tablename__ = "enrolment_pricing_plans"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curriculums.id", ondelete="CASCADE"), nullable=False
    )
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branches.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    monthly_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    start_month: Mapped[int] = mapped_column(nullable=False)
    end_month: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    curriculum: Mapped["Curriculum"] = relationship("Curriculum")
    branch: Mapped["Branch"] = relationship("Branch")
    enrolments: Mapped[list["Enrolment"]] = relationship("Enrolment", back_populates="pricing_plan")
