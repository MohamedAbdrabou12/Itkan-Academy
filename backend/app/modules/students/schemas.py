from datetime import date
from typing import Dict, Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re
from app.modules.users.schemas import UserRead
from app.modules.users.models import UserStatus


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
    national_id: str
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    branch_ids: Optional[List[int]] = None
    password: str
    status: Optional[UserStatus] = UserStatus.pending

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v

    @field_validator("branch_ids")
    def validate_single_branch(cls, v):
        if v and len(v) > 1:
            raise ValueError("Student can be assigned to only one branch.")
        return v

    @field_validator("national_id")
    def validate_national_id(cls, v):
        if not re.match(r"^\d{14}$", v):  # exactly 14 digits, numbers only
            raise ValueError("NationalID must be exactly 14 digits and numeric")
        return v


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    class_ids: Optional[List[int]] = None
    branch_ids: Optional[List[int]] = None
    admission_date: Optional[date] = None
    curriculum_progress: Optional[Dict] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = None

    @field_validator("admission_date")
    @classmethod
    def validate_admission_date(cls, v: Optional[date]) -> Optional[date]:
        from datetime import date as d

        if v and v > d.today():
            raise ValueError("Admission date cannot be in the future")
        return v

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class StudentRead(UserRead):
    student_id: int
    national_id: str
    class_ids: Optional[List[int]] = None
    admission_date: Optional[date]
    curriculum_progress: Optional[Dict]

    class Config:
        from_attributes = True
