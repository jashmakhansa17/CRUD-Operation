from pydantic import BaseModel
from uuid import UUID


# Schemas for Category


class CreateCategory(BaseModel):
    name: str
    parent_id: UUID | None = None


class ReadCategory(BaseModel):
    id: UUID
    name: str
    parent_id: UUID | None
    user_id: UUID

    class Config:
        orm_mode = True


class UpdateCategory(BaseModel):
    name: str | None = None
    parent_id: UUID | None = None


class NestedCategoryResponse(BaseModel):
    id: UUID
    name: str
    patent_id: UUID | None
    user_id: UUID
    subcategories: list["NestedCategoryResponse"] = []

    class Config:
        orm_mode = True
