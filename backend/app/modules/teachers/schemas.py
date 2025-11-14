# backend/app/modules/teachers/schemas.py
from datetime import date, datetime  # noqa
from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead
from app.modules.teachers.models import EmploymentType


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
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    branch_ids: Optional[list[int]] = None
    role_id: Optional[int] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    class_ids: Optional[List[int]] = None
    branch_ids: Optional[list[int]] = None
    role_id: Optional[int] = None

    @field_validator("hire_date")
    @classmethod
    def validate_hire_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Hire date cannot be in the future")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class TeacherRead(UserRead):
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    class_ids: Optional[List[int]] = None

    class Config:
        from_attributes = True
