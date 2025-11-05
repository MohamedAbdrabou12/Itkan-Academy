from datetime import datetime
from typing import Optional

from app.modules.users.models import UserStatus
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    is_active: bool = True
    mfa_enabled: bool = False
    status: UserStatus = UserStatus.pending


class UserCreate(UserBase):
    password: str
    role_id: Optional[int] = None
    branch_id: Optional[int] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    is_active: Optional[bool] = None
    mfa_enabled: Optional[bool] = None
    status: Optional[UserStatus] = None


class UserRead(UserBase):
    id: int
    role_id: Optional[int]
    role_name: Optional[str] = None
    branch_id: Optional[int]
    branch_name: Optional[str] = None
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
