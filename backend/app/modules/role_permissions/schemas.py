from typing import List, Optional

from app.modules.permissions.schemas import Permission
from pydantic import BaseModel, ConfigDict


class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int


class RolePermission(RolePermissionBase):
    permission: Optional[Permission] = None

    class Config:
        from_attributes = True


class PermissionUpdateRequest(BaseModel):
    permission_ids: List[int]


class RolePermissionResponse(BaseModel):
    role_id: int
    permission_id: int
    permission_data: Optional[Permission] = None

    model_config = ConfigDict(from_attributes=True)

