from fastapi import status, Response, Depends
from ..core.dependencies import SessionDep
from ..models.product_model import Product
from ..schemas.product_schema import CreateProduct, UpdateProduct
from sqlmodel import select
from uuid import UUID
from typing import Annotated
from ..core.dependencies import get_current_user
from ..models.user_model import User
from sqlalchemy.exc import IntegrityError
from ..core.exceptions import ItemInvalidDataException, InternalServerException, ItemNotFoundException


class ProductService:

    @staticmethod
    def create_product(product: CreateProduct, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> dict[str, str|int]:

        try:
            db_product = Product(**product.model_dump(), user_id=current_user.id)
            session.add(db_product)
            session.commit()
            session.refresh(db_product)
            return db_product
        
        except IntegrityError as e:
            session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            session.rollback()
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def get_products(session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> list[dict[str, str|int]]:

        try:
            products = session.exec(select(Product).where(Product.user_id == current_user.id)).all()
            if not products:
                raise ItemNotFoundException(type='Product')
            return products
        
        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)
    

    @staticmethod
    def get_pagination_products(
    session: SessionDep,
    current_user: Annotated[User,Depends(get_current_user)],
    page: int = 1, 
    size: int = 10,
    category_id: UUID | None = None, 
    price_min: float | None = None, 
    price_max: float | None = None, 
    ) -> list[dict[str, str|int]]:
        
        try:
            query = select(Product).where(Product.user_id == current_user.id)

            if price_min is not None:
                query = query.where(Product.price >= price_min)
            if price_max is not None:
                query = query.where(Product.price <= price_max)
            if category_id is not None:
                query = query.where(Product.category_id == category_id)

            skip = (page - 1) * size
            query = query.offset(skip).limit(size)

            products = session.exec(query).all()
            if not products:
                raise ItemNotFoundException(type='Product')
            return products
        
        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)
        
    
    @staticmethod
    def get_product(product_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> dict[str, str|int]:
        
        statement = select(Product).where(
            Product.id == product_id, Product.user_id == current_user.id
        )
        product = session.exec(statement).first()

        if not product:
            raise ItemNotFoundException(type='Product', item_id=product_id)
        return product
    

    @staticmethod
    def update_product(product_id: UUID, product_update: UpdateProduct, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> dict[str, str|int]:
        try:

            statement = select(Product).where(
            Product.id == product_id, Product.user_id == current_user.id
            )
            product = session.exec(statement).first()
            
            if not product:
                raise ItemNotFoundException(type='Product',item_id=product_id)
            product_data = product_update.model_dump(exclude_unset=True)
            for key, value in product_data.items():
                setattr(product, key, value)
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
        
        except ItemNotFoundException:
            raise
        
        except IntegrityError as e:
            session.rollback()
            raise ItemInvalidDataException(e)
        
        except Exception as e:
            session.rollback()
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def delete_product(product_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> None:
        
        statement = select(Product).where(
            Product.id == product_id, Product.user_id == current_user.id
        )
        product = session.exec(statement).first()
        
        if not product:
            raise ItemNotFoundException(type='Product',item_id=product_id)
        session.delete(product)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)