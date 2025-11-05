from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.users.models import User
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_permissions(db: AsyncSession, user: User) -> list[str]:
    if not user.role:
        return []

    if getattr(user.role, "permissions", []):
        return [perm.code for perm in user.role.permissions if hasattr(perm, "code")]

    stmt = select(Permission.code).join(Role.permissions).where(Role.id == user.role.id)
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


def require_permission(permission_code: str):
    async def permission_dependency(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role and current_user.role.name.lower() == "admin":
            return

        user_permissions = await get_user_permissions(db, current_user)
        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required permission: {permission_code}",
            )

    return permission_dependency
