from datetime import datetime
from typing import TYPE_CHECKING

from app.db.base import Base
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.modules.curriculums.models.subject_unit_item import SubjectUnitItem
    from app.modules.evaluations.models import Evaluation
    from app.modules.students.models import Student
    from app.modules.exams.models.exam_attempt import ExamAttempt


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    unit_item_id: Mapped[int] = mapped_column(
        ForeignKey("subject_unit_items.id", ondelete="CASCADE"), nullable=False
    )
    evaluation_id: Mapped[int | None] = mapped_column(
        ForeignKey("daily_evaluations.id"), nullable=True
    )
    exam_attempt_id: Mapped[int | None] = mapped_column(ForeignKey("exam_attempts.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    student: Mapped["Student"] = relationship("Student", lazy="selectin")
    unit_item: Mapped["SubjectUnitItem"] = relationship("SubjectUnitItem", lazy="selectin")
    evaluation: Mapped["Evaluation"] = relationship("Evaluation", lazy="selectin")
    exam_attempt: Mapped["ExamAttempt"] = relationship("ExamAttempt", lazy="selectin")
