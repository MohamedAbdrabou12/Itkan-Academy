from decimal import Decimal
from typing import TYPE_CHECKING

from app.db.base import Base
from app.modules.salary.models.payroll_cycles import PayrollCycle
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.users.models import User



class PayrollRecord(Base):
    __tablename__ = "payroll_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    cycle_id: Mapped[int] = mapped_column(ForeignKey("payroll_cycles.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    base_salary: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    allowance: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    bonuses: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal(0))
    deductions: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal(0))

    cycle: Mapped[PayrollCycle] = relationship("PayrollCycle", lazy="selectin")
    employee: Mapped["User"] = relationship("User", lazy="selectin")
