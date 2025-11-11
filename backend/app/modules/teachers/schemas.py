# backend/app/modules/teachers/schemas.py
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
from app.modules.teachers.models import EmploymentType
import re


class TeacherBase(BaseModel):
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    class_ids: Optional[List[int]] = None

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Hire date cannot be in the future")
        return v


class TeacherCreate(TeacherBase):
    # user fields
    name: str
    email: EmailStr
    phone: Optional[str] = None
    branch_id: int

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    class_ids: Optional[List[int]] = None

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Hire date cannot be in the future")
        return v


class TeacherRead(BaseModel):
    id: int
    # user fields
    name: str
    email: str
    phone: Optional[str]
    branch_id: Optional[int]
    role_id: Optional[int]
    status: str
    # teacher-specific
    qualification: Optional[str]
    specialization: Optional[str]
    hire_date: Optional[date]
    employment_type: Optional[EmploymentType]
    class_ids: Optional[List[int]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
