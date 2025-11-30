# backend/app/core/authorization.py
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import get_current_user
from app.db.session import get_db
from app.modules.permissions.models import Permission
from app.modules.roles.models import Role
from app.modules.users.models import User


# PERMISSION RETRIEVAL
async def get_user_permissions(db: AsyncSession, user: User) -> list[str]:
    """
    Returns a list of permission codes for the user's role.
    """
    if not user.role:
        return []

    # Prefer cached relationship if already loaded
    if getattr(user.role, "permissions", []):
        return [perm.code for perm in user.role.permissions if hasattr(perm, "code")]

    # Otherwise, fetch directly from database
    stmt = select(Permission.code).join(Role.permissions).where(Role.id == user.role.id)
    result = await db.execute(stmt)
    return [row[0] for row in result.fetchall()]


# BRANCH ACCESS VALIDATION
def ensure_branch_access(request: Request, current_user: User):
    """
    Ensures the user has access to the branch specified in the X-Branch-ID header.
    Raises HTTP 403 if the user is not authorized for that branch.
    """
    branch_id = getattr(request.state, "active_branch_id", None)
    allowed_branches = getattr(current_user, "branch_ids", [])

    # Global access (admin, superuser) has no branch restrictions
    if not branch_id or not allowed_branches:
        return

    if branch_id not in allowed_branches:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied for branch ID {branch_id}.",
        )


# generate generic permission
def generate_generic_permission(permission_code: str):
    last_dot_index = permission_code.rfind(".")
    if last_dot_index != -1:
        module_name = permission_code[:last_dot_index]
        return f"{module_name}.*"
    else:
        return permission_code


# PERMISSION CHECK DECORATOR
def require_permission(permission_code: str):
    """
    Dependency decorator to enforce a specific permission check.
    Also validates that the current user has access to the active branch.
    """

    async def permission_dependency(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ):
        # Allow admins unrestricted access
        if current_user.role and current_user.role.name.lower() == "admin":
            return

        # Ensure the user can access the active branch
        ensure_branch_access(request, current_user)

        # Check if user has the required permission
        user_permissions = await get_user_permissions(db, current_user)

        # generic permission code
        generic_permission_code = generate_generic_permission(permission_code)
        if (
            permission_code not in user_permissions
            and generic_permission_code not in user_permissions
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required permission: {permission_code}",
            )

    return permission_dependency
