from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead, BranchInfo
from app.modules.users.models import UserStatus


class ParentBase(BaseModel):
    occupation: Optional[str] = None
    address: Optional[str] = None
    relationship_type: str

    @field_validator("relationship_type")
    def validate_relationship_type(cls, v):
        allowed = {"father", "mother", "guardian"}
        if v not in allowed:
            raise ValueError(f"relationship_type must be one of {allowed}")
        return v


class ParentCreate(ParentBase):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class ParentUpdate(BaseModel):
    occupation: Optional[str] = None
    address: Optional[str] = None
    relationship_type: Optional[str] = None

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[UserStatus] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class ParentChildRead(BaseModel):
    student_id: int
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    role_name_ar: Optional[str] = None
    branch_name: Optional[str] = None
    branch_ids: Optional[List[int]] = []
    branches: Optional[List[BranchInfo]] = []
    login_type: Optional[str] = None
    login_identifier: Optional[str] = None
    status: Optional[str] = None
    class_ids: Optional[List[int]] = []
    admission_date: Optional[datetime] = None
    curriculum_progress: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class ParentRead(ParentBase):
    id: int
    user: Optional[UserRead] = None
    children: Optional[List[ParentChildRead]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
