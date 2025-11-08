from datetime import datetime
from typing import Optional

from app.modules.branches.models import BranchStatus
from pydantic import BaseModel


class BranchBase(BaseModel):
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: BranchStatus

    class Config:
        use_enum_values = True


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[BranchStatus]


class BranchRead(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    status: BranchStatus
    created_at: datetime

    class Config:
        from_attributes = True

