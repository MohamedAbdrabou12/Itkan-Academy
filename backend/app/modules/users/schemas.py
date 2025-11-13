# backend/app/modules/users/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.modules.users.models import UserStatus
import re


class BranchInfo(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    # branch_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class UserCreate(UserBase):
    role_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None
    permission_code: Optional[list[int]] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None
    branches: Optional[List[BranchInfo]] = None
    status: Optional[UserStatus] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class UserRead(UserBase):
    id: int
    role_id: Optional[int]
    role_name: Optional[str] = None
    branch_name: Optional[str] = None
    permission_code: Optional[list[int]] | None
    last_login: Optional[datetime] | None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: UserStatus
    branch_ids: Optional[List[int]] = None
    branches: Optional[List[BranchInfo]] = None

    class Config:
        from_attributes = True
