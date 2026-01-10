from pydantic import BaseModel


class Subject(BaseModel):
    id: int
    name: str


class SubjectResponse(Subject):
    pass

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str


class SubjectUpdate(BaseModel):
    name: str
