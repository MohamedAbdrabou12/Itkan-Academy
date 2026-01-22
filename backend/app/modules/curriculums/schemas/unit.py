from app.modules.curriculums.schemas.unit_item import UnitItemResponse
from pydantic import BaseModel


class UnitCreate(BaseModel):
    title: str
    description: str
    subject_id: int
    curriculum_id: int


class UnitUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    subject_id: int | None = None
    curriculum_id: int | None = None


class UnitResponse(BaseModel):
    id: int
    title: str
    description: str
    subject_id: int
    curriculum_id: int

    class Config:
        from_attributes = True


class DetailedUnitResponse(UnitResponse):
    items: list[UnitItemResponse]
    subject_name: str
    curriculum_name: str
