from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.models import User


class EvaluationStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"


class EvaluationCycle(Base):
    """Defines quarterly/yearly evaluation periods."""

    __tablename__ = "evaluation_cycles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "Q1 2026"
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    evaluations: Mapped[List["EmployeeEvaluation"]] = relationship(
        "EmployeeEvaluation", back_populates="cycle", cascade="all, delete-orphan"
    )


class KPITemplate(Base):
    """Reusable group of KPIs (e.g., 'Teacher Quarterly KPIs')."""

    __tablename__ = "kpi_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_global: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    created_by: Mapped[Optional["User"]] = relationship("User", lazy="selectin")
    kpis: Mapped[List["KPI"]] = relationship(
        "KPI", back_populates="template", cascade="all, delete-orphan"
    )
    evaluations: Mapped[List["EmployeeEvaluation"]] = relationship(
        "EmployeeEvaluation", back_populates="template"
    )


class KPI(Base):
    """Individual measurable performance indicators with weights."""

    __tablename__ = "kpis"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("kpi_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False
    )  # Percentage, sum should be 100 per template
    max_score: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    template: Mapped["KPITemplate"] = relationship("KPITemplate", back_populates="kpis")
    scores: Mapped[List["EvaluationKPIScore"]] = relationship(
        "EvaluationKPIScore", back_populates="kpi", cascade="all, delete-orphan"
    )


class EmployeeEvaluation(Base):
    """One evaluation record per employee per cycle."""

    __tablename__ = "employee_evaluations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    employee_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    evaluator_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cycle_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_cycles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_id: Mapped[int] = mapped_column(
        ForeignKey("kpi_templates.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[EvaluationStatus] = mapped_column(
        String(20), default=EvaluationStatus.draft, nullable=False
    )
    final_score: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True
    )  # Calculated when submitted

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    employee: Mapped["User"] = relationship(
        "User", foreign_keys=[employee_user_id], lazy="selectin"
    )
    evaluator: Mapped["User"] = relationship(
        "User", foreign_keys=[evaluator_user_id], lazy="selectin"
    )
    cycle: Mapped["EvaluationCycle"] = relationship(
        "EvaluationCycle", back_populates="evaluations"
    )
    template: Mapped["KPITemplate"] = relationship(
        "KPITemplate", back_populates="evaluations"
    )
    kpi_scores: Mapped[List["EvaluationKPIScore"]] = relationship(
        "EvaluationKPIScore", back_populates="evaluation", cascade="all, delete-orphan"
    )
    comments: Mapped[List["EvaluationComment"]] = relationship(
        "EvaluationComment", back_populates="evaluation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "employee_user_id", "cycle_id", name="uq_employee_evaluation_per_cycle"
        ),
    )


class EvaluationKPIScore(Base):
    """Individual KPI scores for an evaluation."""

    __tablename__ = "evaluation_kpi_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("employee_evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kpi_id: Mapped[int] = mapped_column(
        ForeignKey("kpis.id", ondelete="CASCADE"), nullable=False, index=True
    )
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    evaluation: Mapped["EmployeeEvaluation"] = relationship(
        "EmployeeEvaluation", back_populates="kpi_scores"
    )
    kpi: Mapped["KPI"] = relationship("KPI", back_populates="scores")

    __table_args__ = (
        UniqueConstraint("evaluation_id", "kpi_id", name="uq_evaluation_kpi_score"),
    )


class EvaluationComment(Base):
    """Qualitative feedback for an evaluation."""

    __tablename__ = "evaluation_comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("employee_evaluations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    evaluation: Mapped["EmployeeEvaluation"] = relationship(
        "EmployeeEvaluation", back_populates="comments"
    )
