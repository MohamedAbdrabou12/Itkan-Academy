from pydantic import BaseModel


class CurriculumCreate(BaseModel):
    name: str
    description: str = ""
    academic_year: str
    is_active: bool = True


class CurriculumResponse(BaseModel):
    id: int
    name: str
    description: str
    academic_year: str
    is_active: bool


class CurriculumUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    academic_year: str | None = None
    is_active: bool | None = None
