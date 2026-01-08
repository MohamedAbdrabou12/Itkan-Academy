from app.modules.curriculums.models.unit_item import UnitItemType
from pydantic import BaseModel


class UnitItemResponse(BaseModel):
    id: int
    title: str
    type: UnitItemType
    content: str
    unit_id: int


class UnitItemCreate(BaseModel):
    title: str
    type: UnitItemType
    content: str
    unit_id: int


class UnitItemUpdate(BaseModel):
    title: str | None = None
    type: UnitItemType | None = None
    content: str | None = None
    unit_id: int | None = None
