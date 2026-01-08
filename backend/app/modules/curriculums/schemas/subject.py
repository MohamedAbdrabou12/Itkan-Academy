from pydantic import BaseModel


class SubjectResponse(BaseModel):
    id: int
    name: str


class SubjectCreate(BaseModel):
    name: str


class SubjectUpdate(BaseModel):
    name: str
