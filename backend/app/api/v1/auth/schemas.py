from pydantic import BaseModel, EmailStr, field_validator, model_validator
from app.modules.users.models import UserStatus
from typing import Optional, List
import re


# Registration
class RegisterRequest(BaseModel):
    full_name: str
    national_id: str
    password: str
    phone: str
    email: Optional[EmailStr] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        cleaned = re.sub(r"[^\d+]", "", v)
        if not re.match(r"^\+?\d{10,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned

    @field_validator("national_id")
    def validate_national_id(cls, v):
        if not re.match(r"^\d{14}$", v):
            raise ValueError("NationalID must be exactly 14 digits and numeric")
        return v


# Registration response
class RegisterResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    status: UserStatus

    class Config:
        from_attributes = True


# Branch representation
class Branch(BaseModel):
    id: int
    name: str


# Permission representation
class Permission(BaseModel):
    id: int
    code: str
    description: str


# User representation
class UserRead(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    role_name: Optional[str] = None
    status: UserStatus
    permissions: Optional[List[Permission]] = None
    branches: Optional[List[Branch]] = None

    @model_validator(mode="before")
    @classmethod
    def flatten_from_orm(cls, data):
        if not hasattr(data, "__dict__"):
            return data

        flatten_data = {
            "id": data.id,
            "full_name": data.full_name,
            "email": data.email,
            "status": data.status,
        }
        # Role
        if getattr(data, "role", None):
            flatten_data["role_name"] = data.role.name
            flatten_data["permissions"] = [
                Permission(
                    id=assoc.permission.id,
                    code=assoc.permission.code,
                    description=assoc.permission.description,
                )
                for assoc in getattr(data.role, "permission_associations", [])
                if assoc.permission
            ]
        # Branches
        if getattr(data, "branches", None):
            flatten_data["branches"] = [
                Branch(id=b.id, name=b.name) for b in data.branches
            ]

        return flatten_data

    class Config:
        from_attributes = True


# Auth
class LoginRequest(BaseModel):
    identifier: str
    password: str


# Token response
class TokenResponse(BaseModel):
    access_token: str
    user: UserRead


# Password management
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# Password reset token validation
class ValidateResetTokenRequest(BaseModel):
    token: str


# validate reset token response
class ValidateResetTokenResponse(BaseModel):
    valid: bool
    user_id: Optional[int]


# User activation / status update
class ActivateUserRequest(BaseModel):
    user_id: int
    new_status: UserStatus


# Forgot password request
class ForgotPasswordRequest(BaseModel):
    identifier: str


# Reset password request
class ResetPasswordRequest(BaseModel):
    token: Optional[str] = None
    new_password: str
    user_id: Optional[int] = None


# Common response for password reset actions
class PasswordResetResponse(BaseModel):
    message: str
