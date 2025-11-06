# backend/app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
from app.core.security import verify_password  # noqa F401
from app.db.session import get_db
from app.modules.users.crud import user_crud
from app.modules.users.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession

bearer_scheme = HTTPBearer()

SECRET_KEY: str = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS: int = 90

# Password reset token expiry (in hours)
PASSWORD_RESET_EXPIRE_HOURS: int = 24


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Password Reset Token Management
def create_password_reset_token(
    user_id: int, expires_hours: Optional[int] = None
) -> str:
    """
    Create a signed JWT token for password reset.
    Token payload contains:
      - sub: user id (string)
      - pw_reset: True (marker)
      - exp: expiry datetime
    """
    if expires_hours is None:
        expires_hours = PASSWORD_RESET_EXPIRE_HOURS

    expire = datetime.utcnow() + timedelta(hours=expires_hours)
    payload = {"sub": str(user_id), "pw_reset": True, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_password_reset_token(token: str) -> int:
    """
    Verify a password reset token and return the user_id (int).
    Raises HTTPException(401) on invalid/expired token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired password reset token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise credentials_exception

    sub = payload.get("sub")
    pw_reset = payload.get("pw_reset", False)
    if not sub or not pw_reset:
        raise credentials_exception

    try:
        return int(sub)
    except (TypeError, ValueError):
        raise credentials_exception


# Existing Authentication Methods
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = await user_crud.get_by_id(db, user_id_int)
    if not user:
        raise credentials_exception

    return user


class AuthService:
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        user = await user_crud.get_by_email(db, email)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user

    @staticmethod
    def generate_access_token_for_user(user: User) -> str:
        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email,
            "role_name": user.role.name,
        }
        return create_access_token(token_data)
