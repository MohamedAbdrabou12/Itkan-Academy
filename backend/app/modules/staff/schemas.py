# backend/app/modules/staff/schemas.py
from datetime import datetime  # noqa F401
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead


class StaffBase(BaseModel):
    position: Optional[str] = None
    salary_meta: Optional[Dict] = None
    branch_ids: Optional[List[int]] = None  # updated to many-to-many
    role_id: Optional[int] = None


class StaffCreate(StaffBase):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class StaffUpdate(StaffBase):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class StaffRead(UserRead):
    position: Optional[str] = None
    salary_meta: Optional[Dict] = None

    class Config:
        from_attributes = True
