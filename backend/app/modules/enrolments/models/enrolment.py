from typing import TYPE_CHECKING, final

from app.db.base import Base
from app.modules.enrolments.models.pricing_plan import EnrolmentPricingPlan
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.users.models import User


@final
class Enrolment(Base):
    __tablename__ = "enrolments"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    pricing_plan_id: Mapped[int] = mapped_column(
        ForeignKey("enrolment_pricing_plans.id"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    months_paid: Mapped[int] = mapped_column(nullable=False, default=1)

    pricing_plan: Mapped[EnrolmentPricingPlan] = relationship(
        "EnrolmentPricingPlan", back_populates="enrolments"
    )
    student: Mapped["User"] = relationship("User")
