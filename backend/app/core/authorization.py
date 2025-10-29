from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.core.auth import get_current_user
from app.modules.users.models import User
from app.modules.roles.models import Role
from app.modules.permissions.models.permission import Permission


async def get_user_permissions(db: AsyncSession, user: User):
    """
    Retrieve all permission codes for the given user's role.
    Uses preloaded relationships when available, otherwise queries the DB.
    """
    if not user.role:
        return []

    # Use preloaded relationship if already available
    if getattr(user.role, "permissions", None):
        return [perm.code for perm in user.role.permissions]

    # Fallback: explicit fetch from DB
    stmt = select(Permission.code).join(Role.permissions).where(Role.id == user.role.id)
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


def require_permission(permission_code: str):
    """
    Dependency to ensure the current user has the required permission.

    Example:
        @router.get("/", dependencies=[Depends(require_permission("user:view"))])
    """

    async def permission_dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        # Admin bypass check
        if current_user.role and current_user.role.name.lower() == "admin":
            return

        user_permissions = await get_user_permissions(db, current_user)

        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to perform this action: {permission_code}",
            )

    return permission_dependency
