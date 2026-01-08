from pydantic import BaseModel


class SubjectUnitCreate(BaseModel):
    title: str
    description: str
    subject_id: int


class SubjectUnitUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    subject_id: int | None = None


class SubjectUnitResponse(BaseModel):
    id: int
    title: str
    description: str
    subject_id: int
