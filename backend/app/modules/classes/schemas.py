from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel

class ClassBase(BaseModel):
    branch_id: int
    name: str
    schedule: Dict
    evaluation_config: List[str]


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    branch_id: Optional[int] = None
    name: Optional[str] = None
    schedule: Optional[Dict] = None
    evaluation_config: Optional[Dict] = None


class ClassRead(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassStudentsResponse(BaseModel):
    student_id: int
    full_name: str

    class Config:
        from_attributes = True
