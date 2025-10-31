from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class QuestionBankBase(BaseModel):
    branch_id: Optional[int] = None
    subject: Optional[str] = None
    type: str = "mcq"
    text: str
    options: Optional[Dict] = None
    correct_options: Optional[Dict] = None
    created_by: Optional[int] = None


class QuestionBankCreate(QuestionBankBase):
    pass


class QuestionBankUpdate(BaseModel):
    subject: Optional[str] = None
    type: Optional[str] = None
    text: Optional[str] = None
    options: Optional[Dict] = None
    correct_options: Optional[Dict] = None


class QuestionBankRead(QuestionBankBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
