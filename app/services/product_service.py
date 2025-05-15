from fastapi import status, Response, Depends
from uuid import UUID
from sqlmodel import select
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from ..models.product_model import Product
from ..models.user_model import User
from ..schemas.product_schema import CreateProduct, UpdateProduct
from ..core.dependencies import get_current_user, SessionDep
from ..core.exceptions import (
    ItemInvalidDataException,
    InternalServerException,
    ItemNotFoundException,
)


class ProductService:
    def __init__(
        self,
        session: SessionDep,
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        self.session = session
        self.current_user = current_user

    def create_product(self, product: CreateProduct) -> dict[str, str | int]:
        try:
            db_product = Product(**product.model_dump(), user_id=self.current_user.id)
            self.session.add(db_product)
            self.session.commit()
            self.session.refresh(db_product)
            return db_product

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__)

    def get_products(self) -> list[dict[str, str | int]]:
        try:
            products = self.session.exec(
                select(Product).where(Product.user_id == self.current_user.id)
            ).all()
            if not products:
                raise ItemNotFoundException(type="Product")
            return products

        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)

    def get_pagination_products(
        self,
        page: int = 1,
        size: int = 10,
        category_id: UUID | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
    ) -> list[dict[str, str | int]]:
        try:
            query = select(Product).where(Product.user_id == self.current_user.id)

            if price_min is not None:
                query = query.where(Product.price >= price_min)
            if price_max is not None:
                query = query.where(Product.price <= price_max)
            if category_id is not None:
                query = query.where(Product.category_id == category_id)

            skip = (page - 1) * size
            query = query.offset(skip).limit(size)

            products = self.session.exec(query).all()
            if not products:
                raise ItemNotFoundException(type="Product")
            return products

        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)

    def get_product(self, product_id: UUID) -> dict[str, str | int]:
        statement = select(Product).where(
            Product.id == product_id, Product.user_id == self.current_user.id
        )
        product = self.session.exec(statement).first()

        if not product:
            raise ItemNotFoundException(type="Product", item_id=product_id)
        return product

    def update_product(
        self, product_id: UUID, product_update: UpdateProduct
    ) -> dict[str, str | int]:
        try:
            statement = select(Product).where(
                Product.id == product_id, Product.user_id == self.current_user.id
            )
            product = self.session.exec(statement).first()

            if not product:
                raise ItemNotFoundException(type="Product", item_id=product_id)
            product_data = product_update.model_dump(exclude_unset=True)
            for key, value in product_data.items():
                setattr(product, key, value)
            self.session.add(product)
            self.session.commit()
            self.session.refresh(product)
            return product

        except ItemNotFoundException:
            raise

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__)

    def delete_product(self, product_id: UUID) -> None:
        statement = select(Product).where(
            Product.id == product_id, Product.user_id == self.current_user.id
        )
        product = self.session.exec(statement).first()

        if not product:
            raise ItemNotFoundException(type="Product", item_id=product_id)
        self.session.delete(product)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
