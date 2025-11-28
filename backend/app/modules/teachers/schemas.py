import re
from datetime import date, datetime
from typing import List, Optional

from app.modules.teachers.models import EmploymentType
from app.modules.users.models import UserStatus
from app.modules.users.schemas import BranchInfo
from pydantic import BaseModel, EmailStr, field_validator, model_validator


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


class TeacherRead(BaseModel):
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    hire_date: Optional[date] = None
    employment_type: Optional[EmploymentType] = None
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    role_name_ar: Optional[str] = None
    branch_name: Optional[str] = None
    status: UserStatus
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    branch_ids: Optional[List[int]] = None
    branches: Optional[List[BranchInfo]] = None
    class_ids: Optional[List[int]] = None

    @model_validator(mode="before")
    @classmethod
    def flatten_from_orm(cls, data):
        if hasattr(data, "user"):
            user_details = data.user
            return {
                "full_name": user_details.full_name,
                "email": user_details.email,
                "phone": user_details.phone,
                "role_id": user_details.role_id,
                "role_name": user_details.role_name,
                "role_name_ar": user_details.role_name_ar,
                "branch_name": user_details.branch_name,
                "status": user_details.status,
                "last_login": user_details.last_login,
                "created_at": user_details.created_at,
                "updated_at": user_details.updated_at,
                "branch_ids": [link.branch_id for link in user_details.branch_links],
                "branches": user_details.branches,
                "class_ids": [c.id for c in data.classes] if data.classes else [],
                "qualification": data.qualification,
                "specialization": data.specialization,
                "hire_date": data.hire_date,
                "employment_type": data.employment_type,
                "id": user_details.id,
            }
        return data

    class Config:
        from_attributes = True
