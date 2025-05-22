from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)


class UpdateCategory(BaseModel):
    name: str | None = None
    parent_id: UUID | None = None


class NestedCategoryResponse(BaseModel):
    id: UUID
    name: str
    parent_id: UUID | None
    user_id: UUID
    subcategories: list["NestedCategoryResponse"] = []

    model_config = ConfigDict(from_attributes=True)


NestedCategoryResponse.model_rebuild()