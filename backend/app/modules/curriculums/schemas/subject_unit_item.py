from app.modules.curriculums.models.subject_unit_item import SubjectUnitItemType
from pydantic import BaseModel


class SubjectUnitItemResponse(BaseModel):
    id: int
    title: str
    type: SubjectUnitItemType
    content: str
    unit_id: int


class SubjectUnitItemCreate(BaseModel):
    title: str
    type: SubjectUnitItemType
    content: str
    unit_id: int


class SubjectUnitItemUpdate(BaseModel):
    title: str | None = None
    type: SubjectUnitItemType | None = None
    content: str | None = None
    unit_id: int | None = None
