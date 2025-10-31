from datetime import datetime
from typing import Optional, List  # noqa F401
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

    class Config:
        from_attributes = True
