from app.modules.curriculums.schemas.unit import DetailedUnitResponse
from pydantic import BaseModel


class Subject(BaseModel):
    id: int
    name: str


class SubjectResponse(Subject):
    class Config:
        from_attributes = True


class DetailedSubjectResponse(SubjectResponse):
    units: list[DetailedUnitResponse]


class SubjectCreate(BaseModel):
    name: str


class SubjectUpdate(BaseModel):
    name: str
