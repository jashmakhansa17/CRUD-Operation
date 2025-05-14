from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from .product_model import Product


class Category(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False, unique=True)

    user_id: UUID | None = Field(foreign_key='people.id', ondelete='CASCADE')
    parent_id: UUID | None = Field(default=None, foreign_key='category.id', ondelete='CASCADE')
    subcategories: list['Category'] = Relationship()
    products: list["Product"] = Relationship()
    