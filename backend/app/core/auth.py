from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import verify_password
from app.db.session import get_db
from app.modules.users.crud import user_crud
from app.modules.users.models import User

# CONFIGURATION
bearer_scheme = HTTPBearer()
SECRET_KEY: str = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS: int = 90
PASSWORD_RESET_EXPIRE_HOURS: int = 24


# TOKEN CREATION
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with optional expiration.
    The token may include:
      - sub: user_id
      - email
      - role_name
      - branch_ids: list of accessible branches
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# AUTHENTICATION HELPERS
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extracts authenticated user from JWT token.
    Token does NOT depend on branch_id — branch context handled via X-Branch-ID header.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise credentials_exception

    user = await user_crud.get_by_id(db, user_id)
    if not user:
        raise credentials_exception

    # Attach branch_ids for middleware usage
    user.branch_links = payload.get("branch_ids", [])
    return user


# AUTH SERVICE
class AuthService:
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """
        Verify user credentials against database.
        Returns User object or None if invalid.
        """
        user = await user_crud.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def generate_access_token_for_user(user: User) -> str:
        permission_codes = []
        if user.role and user.role.permission_associations:
            permission_codes = [
                {
                    "id": assoc.permission.id,
                    "code": assoc.permission.code,
                    "description": assoc.permission.description,
                }
                for assoc in user.role.permission_associations
                if assoc.permission
            ]
        token_data = {
            "sub": str(user.id),
            "user_id": user.id,
            "email": user.email,
            "role_name": getattr(user.role, "name", None),
            "branches": [
                {"id": b.id, "name": b.name} for b in getattr(user, "branches", [])
            ]
            if getattr(user, "branches", None)
            else [],
            "permissions": permission_codes,
        }
        return create_access_token(token_data)
