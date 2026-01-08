from datetime import datetime

from app.modules.classes.models import ClassStatus
from pydantic import BaseModel


class ClassBase(BaseModel):
    branch_id: int
    curriculum_id: int
    subject_id: int
    name: str
    schedule: dict
    evaluation_config: list[str]


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    branch_id: int | None = None
    curriculum_id: int | None = None
    subject_id: int | None = None
    name: str | None = None
    schedule: dict | None = None
    evaluation_config: list[str] | None = None


class ClassRead(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: ClassStatus | None = None

    class Config:
        from_attributes = True


class ClassStudentsResponse(BaseModel):
    student_id: int
    full_name: str

    class Config:
        from_attributes = True
