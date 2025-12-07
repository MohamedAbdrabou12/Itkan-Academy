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
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    branch_ids: Optional[List[int]] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class UserCreate(UserBase):
    role_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None
    status: Optional[UserStatus]
    login_identifier: str
    login_type: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    branch_ids: Optional[List[int]] = None
    branches: Optional[List[BranchInfo]] = None
    status: Optional[UserStatus] = None
    login_identifier: Optional[str] = None
    login_type: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if v:
            cleaned = re.sub(r"[^\d+]", "", v)
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValueError("Invalid phone number format")
            return cleaned
        return v


class UserRoleUpdate(BaseModel):
    user_id: int
    role_id: int


class UserRead(UserBase):
    id: int
    role_id: Optional[int]
    role_name: Optional[str] = None
    role_name_ar: Optional[str] = None
    branch_name: Optional[str] = None
    last_login: Optional[datetime] | None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: UserStatus
    branch_ids: Optional[List[int]] = None
    branches: Optional[List[BranchInfo]] = None
    login_identifier: str
    login_type: str

    class Config:
        from_attributes = True


# from datetime import datetime
# from typing import Optional, List
# from pydantic import BaseModel, EmailStr, field_validator
# from app.modules.users.models import UserStatus
# import re


# class BranchInfo(BaseModel):
#     id: int
#     name: Optional[str] = None

#     class Config:
#         from_attributes = True


# class UserBase(BaseModel):
#     full_name: str
#     email: EmailStr
#     phone: Optional[str] = None
#     branch_ids: Optional[List[int]] = None

#     @field_validator("phone")
#     def validate_phone(cls, v):
#         if v:
#             cleaned = re.sub(r"[^\d+]", "", v)
#             if not re.match(r"^\+?\d{10,15}$", cleaned):
#                 raise ValueError("Invalid phone number format")
#             return cleaned
#         return v


# class UserCreate(UserBase):
#     role_id: Optional[int] = None
#     branch_ids: Optional[List[int]] = None
#     status: Optional[UserStatus]


# class UserUpdate(BaseModel):
#     full_name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     phone: Optional[str] = None
#     password: Optional[str] = None
#     role_id: Optional[int] = None
#     branch_ids: Optional[List[int]] = None
#     branches: Optional[List[BranchInfo]] = None
#     status: Optional[UserStatus] = None

#     @field_validator("phone")
#     def validate_phone(cls, v):
#         if v:
#             cleaned = re.sub(r"[^\d+]", "", v)  # remove spaces, - , etc
#             if not re.match(r"^\+?\d{10,15}$", cleaned):
#                 raise ValueError("Invalid phone number format")
#             return cleaned
#         return v


# class UserRoleUpdate(BaseModel):
#     user_id: int
#     role_id: int


# class UserRead(UserBase):
#     id: int
#     role_id: Optional[int]
#     role_name: Optional[str] = None
#     role_name_ar: Optional[str] = None
#     branch_name: Optional[str] = None
#     last_login: Optional[datetime] | None
#     created_at: Optional[datetime] = None
#     updated_at: Optional[datetime] = None
#     status: UserStatus
#     branch_ids: Optional[List[int]] = None
#     branches: Optional[List[BranchInfo]] = None

#     class Config:
#         from_attributes = True
