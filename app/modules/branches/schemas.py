from pydantic import BaseModel


class BranchOut(BaseModel):
    id: int
    name: str
    address: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class BranchCreate(BaseModel):
    name: str
    address: str | None = None


class BranchUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    is_active: bool | None = None
