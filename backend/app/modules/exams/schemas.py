from pydantic import BaseModel
from datetime import datetime


class ExamCreate(BaseModel):
    title: str
    description: str | None = None
    created_by: int


class ExamOut(BaseModel):
    id: int
    title: str
    description: str | None
    created_at: datetime | None
    created_by: int

    class Config:
        orm_mode = True
