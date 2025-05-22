from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from uuid import UUID, uuid4
from .product_model import Product


class Category(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_category_name_user"),
    )

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, nullable=False)

    user_id: UUID | None = Field(foreign_key="people.id", ondelete="CASCADE")
    parent_id: UUID | None = Field(
        default=None, foreign_key="category.id", ondelete="CASCADE"
    )
    subcategories: list["Category"] = Relationship()
    products: list["Product"] = Relationship()
    
