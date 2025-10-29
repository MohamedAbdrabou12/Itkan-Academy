# app/modules/permissions/schemas/permission_role.py
from pydantic import BaseModel
from typing import Optional


class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionRead(RolePermissionBase):
    role_name: Optional[str] = None
    permission_code: Optional[str] = None

    class Config:
        from_attributes = True
