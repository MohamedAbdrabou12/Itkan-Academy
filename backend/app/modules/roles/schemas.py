# # app/modules/roles/schemas/role.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.modules.permissions.schemas.permission import PermissionRead


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleRead(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionRead] = []

    class Config:
        from_attributes = True
