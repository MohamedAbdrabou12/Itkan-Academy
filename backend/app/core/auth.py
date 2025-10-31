# app/core/auth.py
# app/core/auth.py
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.users.models import User, UserStatus
from app.modules.users.crud import user_crud
from app.core.config import settings
from app.core.security import verify_password, get_password_hash  # noqa F401


bearer_scheme = HTTPBearer()

SECRET_KEY: str = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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

    if user.status != UserStatus.active or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not active or awaiting approval.",
        )

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

        if user.status != UserStatus.active or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is pending approval or inactive.",
            )

        return user

    @staticmethod
    def generate_token_for_user(user: User) -> str:
        return create_access_token({"sub": str(user.id)})
