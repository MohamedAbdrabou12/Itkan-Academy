from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

if TYPE_CHECKING:
    from .exam import Exam
    from app.modules.question_bank.models import QuestionBank
    from app.modules.branches.models import Branch
    from .exam_answer import ExamAnswer


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)

    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("question_bank.id"))
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"))

    # Relationships
    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")
    question: Mapped["QuestionBank"] = relationship("QuestionBank")

    answers: Mapped[List["ExamAnswer"]] = relationship(
        "ExamAnswer", back_populates="question"
    )

    __table_args__ = (
        UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
        UniqueConstraint("exam_id", "order", name="uq_exam_question_order"),
    )
