from datetime import datetime
from typing import Optional
from pydantic import BaseModel, model_validator
from .models import QuestionDifficulty, QuestionType


class QuestionOption(BaseModel):
    key: str
    option: str


class QuestionBankBase(BaseModel):
    title: str
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    type: QuestionType = QuestionType.MCQ
    options: Optional[list[QuestionOption]] = None
    correct_answer: Optional[str] = None


class QuestionBankCreate(QuestionBankBase):
    @model_validator(mode="after")
    def validate_mcq_questions(self):
        # validate options for MCQ type questions
        if self.type == QuestionType.MCQ:
            if not self.options or len(self.options) < 2 or len(self.options) > 6:
                raise ValueError(
                    "السؤال من النوع اختيار من متعدد يجب ان يحتوى من 2 الى 6 خيارات"
                )

            # Validate correct_option
            if self.correct_answer is None:
                raise ValueError("يحب اخيار الاجابة الصحيحة")
        elif self.type in {QuestionType.SHORT_ANSWER, QuestionType.ESSAY}:
            if self.options is not None:
                raise ValueError("خيارات السؤال غير مطلوبة في هذا النوع")
            if self.correct_answer is not None:
                raise ValueError("الاجابة الصحيحة غير مطلوبة في هذا النوع")

        return self


class QuestionBankRead(QuestionBankBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
