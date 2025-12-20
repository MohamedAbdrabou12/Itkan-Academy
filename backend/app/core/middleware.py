from typing import Optional, Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import jwt, JWTError
from sqlalchemy.future import select
from fastapi import HTTPException, status
import logging
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.modules.users.models import User
from sqlalchemy.orm import selectinload


# CONFIGURATION
SECRET_KEY = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM = "HS256"
logger = logging.getLogger(__name__)


# MIDDLEWARE CLASS
class BranchContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
      - Extracts the authenticated user from the JWT token.
      - Reads the active branch from the X-Branch-ID header.
      - Validates that the user has access to the selected branch.
      - Admin users bypass branch checks.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[..., Any]
    ) -> Response:
        # Safe initialization
        request.state.current_user = None
        request.state.active_branch_id = None
        request.state.branch_ids = []

        # Extract user from Bearer token
        auth_header: Optional[str] = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("user_id") or payload.get("sub")

                if user_id:
                    async with AsyncSessionLocal() as db:
                        stmt = (
                            select(User)
                            .where(User.id == int(user_id))
                            .options(
                                selectinload(User.role),
                            )
                        )
                        result = await db.execute(stmt)
                        user = result.scalars().first()
                        if user:
                            request.state.current_user = user
                            request.state.branch_ids = payload.get("branch_ids", [])
            except JWTError as e:
                logger.warning(f"JWT decode error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in middleware: {e}")

        # Read X-Branch-ID from headers
        branch_id_header = request.headers.get("X-Branch-ID")
        if branch_id_header:
            try:
                branch_id = int(branch_id_header)
                request.state.active_branch_id = branch_id

                allowed = getattr(request.state, "branch_ids", [])
                current_user = getattr(request.state, "current_user", None)

                # Skip check if admin
                if current_user and getattr(current_user, "role_name", None) == "admin":
                    pass
                else:
                    # If user has restricted branches and selected one outside allowed list
                    if allowed and branch_id not in allowed:
                        logger.warning(
                            f"User {getattr(current_user, 'id', None)} "
                            f"attempted access to unauthorized branch {branch_id}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don’t have access to this branch.",
                        )

            except ValueError:
                logger.warning(f"Invalid X-Branch-ID header: {branch_id_header}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid X-Branch-ID header format. Must be an integer.",
                )

        # Continue request processing
        response = await call_next(request)
        return response


# UTILITY HELPERS
def get_branch_filter(request: Request) -> Optional[Callable[[Any], Any]]:
    """
    Returns a SQLAlchemy filter function for the active branch.
    If no branch context, returns None (global query scope).
    """
    active_branch = getattr(request.state, "active_branch_id", None)

    def filter_query(query: Any) -> Any:
        return query.filter_by(branch_id=active_branch)

    return filter_query if active_branch is not None else None


def ensure_user_branch_access(request: Request, branch_id: Optional[int]) -> None:
    """
    Validates that the user can access a given branch.
    Admin users bypass this check.
    Raises HTTP 403 if access is not allowed.
    """
    current_user = getattr(request.state, "current_user", None)
    allowed_branches = getattr(request.state, "branch_ids", [])

    # Admin bypass
    if current_user and getattr(current_user, "role_name", None) == "admin":
        return

    if not allowed_branches or branch_id in allowed_branches:
        return

    logger.warning(
        f"User {getattr(current_user, 'id', None)} denied access to branch {branch_id}"
    )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied for this branch.",
    )


async def get_current_branch(request: Request) -> Optional[int]:
    """
    Dependency to retrieve the current active branch ID
    from the request context. Raises 400 if missing.
    """
    branch_id = getattr(request.state, "active_branch_id", None)
    if branch_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing branch context. Please include X-Branch-ID header.",
        )
    return branch_id
