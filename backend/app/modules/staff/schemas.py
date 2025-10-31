from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel


class StaffBase(BaseModel):
    user_id: int
    branch_id: int
    position: Optional[str] = None
    salary_meta: Optional[Dict] = None


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    branch_id: Optional[int] = None
    position: Optional[str] = None
    salary_meta: Optional[Dict] = None


class StaffRead(StaffBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
