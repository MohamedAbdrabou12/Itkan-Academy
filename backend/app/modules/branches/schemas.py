# backend/app/modules/branches/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: Optional[bool] = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    active: Optional[bool] = None


class BranchRead(BranchBase):
    id: int
    created_at: datetime
    updated_at: datetime
    users_count: Optional[int] = None  # Optional enhancement

    class Config:
        from_attributes = True
