# backend/app/modules/students/schemas.py
from datetime import date, datetime  # noqa F401
from typing import Dict, Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead


class StudentBase(BaseModel):
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
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    branch_ids: Optional[List[int]] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?\d{10,15}$", v):
            raise ValueError("Invalid phone number format")
        return v

    # validate that only one branch is assigned for student
    @field_validator("branch_ids")
    def validate_single_branch(cls, v):
        if v:
            if len(v) > 1:
                raise ValueError("Student can be assigned to only one branch.")
        return v


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    class_ids: Optional[List[int]] = None
    branch_ids: Optional[List[int]] = None
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


class StudentRead(UserRead):
    class_ids: Optional[List[int]] = None
    admission_date: Optional[date]
    curriculum_progress: Optional[Dict]

    class Config:
        from_attributes = True
