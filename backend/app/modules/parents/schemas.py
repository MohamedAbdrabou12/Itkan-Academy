# app/modules/parents/schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead
from app.modules.students.schemas import StudentRead
from app.modules.users.models import UserStatus


class ParentBase(BaseModel):
    occupation: Optional[str] = None
    address: Optional[str] = None
    relationship_type: str  # required: 'father'|'mother'|'guardian'

    @field_validator("relationship_type")
    def validate_relationship_type(cls, v):
        allowed = {"father", "mother", "guardian"}
        if v not in allowed:
            raise ValueError(f"relationship_type must be one of {allowed}")
        return v


class ParentCreate(ParentBase):
    # We create linked user at same time (no branches)
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: Optional[str] = None

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

    # optional user updates
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    status: Optional[UserStatus] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class ParentMini(BaseModel):
    id: int
    user: UserRead

    class Config:
        from_attributes = True


class ParentRead(ParentBase):
    id: int
    user: UserRead
    children: Optional[List[StudentRead]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
