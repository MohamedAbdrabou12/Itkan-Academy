from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PermissionBase(BaseModel):
    code: str
    name: str
    name_ar: str
    description: Optional[str] = None
    description_ar: Optional[str] = None


class Permission(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(PermissionBase):
    pass


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


class RolePermissionsResponse(BaseModel):
    role_permissions: List[RolePermissionResponse]
    available_permissions: List[Permission]
