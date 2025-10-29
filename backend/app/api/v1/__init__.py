from fastapi import APIRouter

# Import routers from modules
from app.modules.users.router import router as user_router
from app.modules.roles.router import router as role_router
from app.modules.permissions.router.permission import router as permission_router
from app.modules.permissions.router.permission_role import (
    router as role_permission_router,
)

# Initialize API Router
api_router = APIRouter()

# Include sub-routers with tags for Swagger grouping
api_router.include_router(user_router, tags=["Users"])
api_router.include_router(role_router, tags=["Roles"])
api_router.include_router(permission_router, tags=["Permissions"])
api_router.include_router(role_permission_router, tags=["Role Permissions"])
