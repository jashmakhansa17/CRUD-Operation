from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

# Schemas for Product


class CreateProduct(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    category_id: UUID


class ReadProduct(BaseModel):
    id: UUID
    name: str
    description: str
    price: float
    category_id: UUID
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class UpdateProduct(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category_id: UUID | None = None
