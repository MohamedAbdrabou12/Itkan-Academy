from datetime import datetime
from typing import List, Optional

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
    users_count: Optional[int] = 0

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    page: int
    pageSize: int
    total: int
    totalPages: int


class BranchesResponse(BaseModel):
    branches: List[BranchRead]
    pagination: PaginationInfo
