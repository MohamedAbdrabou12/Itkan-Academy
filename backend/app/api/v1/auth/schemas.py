# backend/app/api/v1/auth/schemas.py
from pydantic import BaseModel, EmailStr
from app.modules.users.models import UserStatus
from typing import Optional


# Registration
class RegisterRequest(BaseModel):
    name: str
    parent_name: str
    email: EmailStr
    password: str
    phone: str


# User representation
class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role_name: str
    status: UserStatus
    branch_id: Optional[int] = None  # Add this line

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
