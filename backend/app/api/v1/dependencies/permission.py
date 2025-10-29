from fastapi import Depends, HTTPException, status
from app.api.v1.dependencies.auth import get_current_user


async def has_permission(
    required_permission: str, user: dict = Depends(get_current_user)
):
    user_permissions = user.get("permissions", [])
    if required_permission not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{required_permission}' required",
        )
    return True
