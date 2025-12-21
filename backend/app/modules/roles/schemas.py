from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    name_ar: str
    description: str
    description_ar: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    name_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class PermissionSimple(BaseModel):
    id: int
    code: str
    name: str
    name_ar: str

    class Config:
        from_attributes = True


class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionSimple] = []

    class Config:
        from_attributes = True


class RoleRead(BaseModel):
    id: int
    name: str
    description: str
    description_ar: str
    name_ar: str
    created_at: datetime
    permissions_count: int
    # updated_at: datetime
    # permissions: List[PermissionRead] = []

    class Config:
        from_attributes = True
