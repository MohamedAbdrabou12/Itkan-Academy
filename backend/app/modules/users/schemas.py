# app/modules/users/schemas.py
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

    class Config:
        orm_mode = True
