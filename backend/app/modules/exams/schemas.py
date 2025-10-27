from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ExamCreate(BaseModel):
    title: str
    description: str | None = None
    created_by: int

    model_config = ConfigDict(extra="ignore")


class ExamOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    created_at: datetime | None = None
    created_by: int

    model_config = ConfigDict(from_attributes=True)
