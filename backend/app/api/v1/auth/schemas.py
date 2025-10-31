from pydantic import BaseModel, EmailStr
from app.modules.users.models import UserStatus


# Registration
class RegisterRequest(BaseModel):
    name: str
    parent_name: str
    email: EmailStr
    password: str
    phone: str
    branch_id: int


# User representation
class UserRead(BaseModel):
    id: int
    name: str
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


# User activation / status update
class ActivateUserRequest(BaseModel):
    user_id: int
    new_status: UserStatus
