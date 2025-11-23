# backend/app/api/v1/auth/schemas.py
from pydantic import BaseModel, EmailStr
from app.modules.users.models import UserStatus
from typing import Optional
from pydantic import field_validator
import re


# Registration
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: str

    # @field_validator("phone")
    # def validate_phone(cls, v):
    #     if v and not re.match(r"^\+?\d{10,15}$", v):
    #         raise ValueError("Invalid phone number format")
    #     return v


@field_validator("phone")
def validate_phone(cls, v):
    if v:
        cleaned = re.sub(r"[^\d+]", "", v)  # remove spaces, - , etc
        if not re.match(r"^\+?\d{10,15}$", cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned
    return v


# User representation
class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role_name: str
    status: UserStatus

    class Config:
        from_attributes = True


# Login request and token response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    user: UserRead


# Password management
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ValidateResetTokenRequest(BaseModel):
    token: str


class ValidateResetTokenResponse(BaseModel):
    valid: bool
    user_id: Optional[int]


# User activation / status update
class ActivateUserRequest(BaseModel):
    user_id: int
    new_status: UserStatus


# Forgot password request
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Reset password request
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


# Common response for password reset actions
class PasswordResetResponse(BaseModel):
    message: str
