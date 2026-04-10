from datetime import datetime, timedelta
from typing import Annotated, Optional

from app.core.config import settings
from fastapi import Header, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt  # type: ignore

bearer_scheme = HTTPBearer()

SECRET_KEY: str = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS: int = 90

# Password reset token expiry (in hours)
PASSWORD_RESET_EXPIRE_HOURS: int = 24


# Password Reset Token Management
def create_password_reset_token(user_id: int, expires_hours: Optional[int] = None) -> str:
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


async def get_active_branch_id(
    x_branch_id: Annotated[Optional[str], Header(alias="X-Branch-ID")] = None,
) -> int:
    if not x_branch_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Branch-ID header is required",
        )

    try:
        return int(x_branch_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid branch ID format - must be an integer",
        )
