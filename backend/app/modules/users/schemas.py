# backend/app/modules/users/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.modules.users.models import UserStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    branch_id: Optional[int] = None
    status: UserStatus = UserStatus.pending


class UserCreate(UserBase):
    role_id: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    status: Optional[UserStatus] = None


class UserRead(UserBase):
    id: int
    role_id: Optional[int]
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    permission_code: Optional[str] = None
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
