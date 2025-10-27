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

    model_config = {
        "from_attributes": True  # enable ORM mode in Pydantic v2
    }
