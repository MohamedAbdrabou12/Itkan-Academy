# backend/app/modules/students/schemas.py
from datetime import date, datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re


class StudentBase(BaseModel):
    parent_name: str
    class_ids: Optional[List[int]] = None
    admission_date: Optional[date] = None
    curriculum_progress: Optional[Dict] = None

    @field_validator("admission_date")
    @classmethod
    def validate_admission_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Admission date cannot be in the future")
        return v


class StudentCreate(StudentBase):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    branch_id: int

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    parent_name: Optional[str] = None
    class_ids: Optional[List[int]] = None
    branch_id: Optional[int] = None
    admission_date: Optional[date] = None
    curriculum_progress: Optional[Dict] = None

    @field_validator("admission_date")
    @classmethod
    def validate_admission_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Admission date cannot be in the future")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class StudentRead(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role_id: Optional[int]
    branch_id: Optional[int]
    status: str
    parent_name: str
    class_ids: Optional[List[int]] = None
    admission_date: Optional[date]
    curriculum_progress: Optional[Dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
