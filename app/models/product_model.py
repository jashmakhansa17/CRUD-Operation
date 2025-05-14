from sqlmodel import SQLModel, Field
from sqlalchemy import UniqueConstraint, CheckConstraint
from uuid import UUID, uuid4


class Product(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "category_id", name="uq_product_name_category"),
        CheckConstraint("price > 0", name="chk_price_positive"),
    )

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    price: float = Field(gt=0)

    category_id: UUID | None = Field(foreign_key='category.id', ondelete='CASCADE')
