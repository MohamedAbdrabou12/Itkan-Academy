# backend/app/core/middleware.py
from typing import Optional, Callable, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from jose import jwt, JWTError
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.modules.users.models import User

SECRET_KEY = settings.SECRET_KEY or "dev-secret-key"
ALGORITHM = "HS256"


class BranchScopeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract the logged-in user from JWT and attach
    current_user and branch_id to request.state for downstream access.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[..., Any]
    ) -> Response:
        # Define attributes safely
        request.state.current_user = None
        request.state.branch_id = None

        auth_header: Optional[str] = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("user_id") or payload.get("sub")
                if user_id:
                    try:
                        user_id_int = int(user_id)
                        async with AsyncSessionLocal() as db:
                            stmt = select(User).where(User.id == user_id_int)
                            result = await db.execute(stmt)
                            user = result.scalars().first()
                            if user:
                                request.state.current_user = user
                                # branch_id might be None (e.g., admin users)
                                request.state.branch_id = getattr(
                                    user, "branch_id", None
                                )
                    except (TypeError, ValueError):
                        pass
            except JWTError:
                pass

        response = await call_next(request)
        return response


def get_branch_filter(request: Request) -> Optional[Callable[[Any], Any]]:
    """
    Utility: returns a SQLAlchemy query filter function based on the user's branch_id.
    If branch_id is None (admins/managers), returns None (no filtering).
    """
    branch_id = getattr(request.state, "branch_id", None)

    def filter_query(query: Any) -> Any:
        return query.filter_by(branch_id=branch_id)

    return filter_query if branch_id is not None else None
