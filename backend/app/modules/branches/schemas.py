from pydantic import BaseModel


class BranchCreate(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None


class BranchOut(BaseModel):
    id: int
    name: str
    address: str | None = None
    phone: str | None = None

    class Config:
        orm_mode = True
