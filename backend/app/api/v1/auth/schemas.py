# backend/app/api/v1/auth/schemas.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.modules.users.models import UserStatus


# Login request and token response
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None


# Registration
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_id: Optional[int] = None


# User representation
class UserRead(BaseModel):
    id: int
    full_name: str
    email: str
    role_name: Optional[str] = None
    status: UserStatus

    class Config:
        from_attributes = True


# Password management
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


# User activation / status update
class ActivateUserRequest(BaseModel):
    user_id: int
    new_status: UserStatus
