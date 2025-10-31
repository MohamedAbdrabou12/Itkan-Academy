from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel


class ClassBase(BaseModel):
    branch_id: int
    name: str
    schedule: Optional[Dict] = None


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    branch_id: Optional[int] = None
    name: Optional[str] = None
    schedule: Optional[Dict] = None


class ClassRead(ClassBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
