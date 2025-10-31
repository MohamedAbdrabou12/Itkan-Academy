from typing import Optional

from pydantic import BaseModel


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
