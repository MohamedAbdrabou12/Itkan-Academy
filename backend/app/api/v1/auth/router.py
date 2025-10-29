from fastapi import APIRouter, HTTPException, Depends  # noqa
from pydantic import BaseModel
from datetime import timedelta  # noqa

from app.api.v1.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


# simple login endpoint for demonstration purposes
class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(data: LoginRequest):
    # TODO: validate user credentials against the database
    if data.email != "admin@example.com" or data.password != "1234":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {"sub": data.email, "permissions": ["view_users", "manage_roles"]}
    )
    return {"access_token": token, "token_type": "bearer"}
