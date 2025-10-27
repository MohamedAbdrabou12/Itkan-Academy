# app/modules/users/schemas.py
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    is_active: bool

    # Pydantic V2: use 'from_attributes' instead of 'orm_mode'
    model_config = ConfigDict(from_attributes=True)
