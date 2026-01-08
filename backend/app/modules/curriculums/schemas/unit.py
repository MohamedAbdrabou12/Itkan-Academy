from pydantic import BaseModel


class UnitCreate(BaseModel):
    title: str
    description: str
    subject_id: int


class UnitUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    subject_id: int | None = None


class UnitResponse(BaseModel):
    id: int
    title: str
    description: str
    subject_id: int
