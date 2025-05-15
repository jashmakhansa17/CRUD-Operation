from fastapi import status, Response, Depends
from ..core.dependencies import SessionDep
from ..models.category_model import Category
from ..schemas.category_schema import CreateCategory, UpdateCategory, NestedCategoryResponse
from sqlmodel import select
from uuid import UUID
from typing import Annotated
from ..models.user_model import User
from ..core.dependencies import admin_access, get_current_user

from sqlalchemy.exc import IntegrityError
from ..core.exceptions import ItemInvalidDataException, InternalServerException, ItemNotFoundException
 

class CategoryService:

    @staticmethod
    def create_category(category: CreateCategory, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> dict[str, str | int | None]:
        try:
            db_category = Category(**category.model_dump(),user_id=current_user.id)
            session.add(db_category)
            session.commit()
            session.refresh(db_category)
            return db_category
        
        except IntegrityError as e:
            session.rollback()
            raise ItemInvalidDataException(e)
        
        except Exception as e:
            session.rollback()
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def get_categories(session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> list[dict[str, str | int | None]]:
        try:
            categories = session.exec(select(Category).where(Category.user_id == current_user.id)).all()
            if not categories:
                raise ItemNotFoundException(type='Category')
            return categories
        
        except ItemNotFoundException:
            raise
        
        except Exception as e:
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def get_pagination_categories(
    session: SessionDep,
    current_user: Annotated[User,Depends(get_current_user)],
    page: int = 1, 
    size: int = 10,
    parent_id: UUID | None = None, 
    ) -> list[dict[str, str | int | None]]:
        try:
            query = select(Category).where(Category.user_id == current_user.id)

            if parent_id is not None:
                query = query.where(Category.parent_id == parent_id)

            skip = (page - 1) * size
            query = query.offset(skip).limit(size)

            categories = session.exec(query).all()
            if not categories:
                raise ItemNotFoundException(type='Category')
            return categories
        
        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)
        

    # dependency for nested category
    @staticmethod
    def get_nested_categories(category: Category, user_id: UUID) -> dict:

        if category.user_id != user_id:
            return None

        result = {
            'id':category.id,
            'name':category.name,
            'parent_id':category.parent_id,
            'subcategories': [
                sub for sub in (
                    CategoryService.get_nested_categories(sub, user_id) 
                    for sub in category.subcategories
                ) if sub
            ]
        }
        return result
    

    @staticmethod
    def nested_category(category_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> NestedCategoryResponse:
        try:
            
            statement = select(Category).where(
            Category.id == category_id,
            Category.user_id == current_user.id
            )
            category = session.exec(statement).first()
            
            if not category:
                raise ItemNotFoundException(type='Category', item_id=category_id)
            return CategoryService.get_nested_categories(category, current_user.id)
        
        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def read_category(category_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> dict[str, str | int | None]:
        
        statement = select(Category).where(
            Category.id == category_id, Category.user_id == current_user.id
        )
        category = session.exec(statement).first()

        if not category:
            raise ItemNotFoundException(type='Category', item_id=category_id)
        return category
    

    @staticmethod
    def update_category(category_id: UUID, category_update: UpdateCategory, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> dict[str, str | int | None]:
        try:

            statement = select(Category).where(
            Category.id == category_id, Category.user_id == current_user.id
            )
            category = session.exec(statement).first()

            if not category:
                raise ItemNotFoundException(type='Category', item_id=category_id)
            category_data = category_update.model_dump(exclude_unset=True)
            for key, value in category_data.items():
                setattr(category, key, value)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
        
        except ItemNotFoundException:
            raise
        
        except IntegrityError as e:
            session.rollback()
            raise ItemInvalidDataException(e)
        
        except Exception as e:
            session.rollback()
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def delete_category(category_id: UUID, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> None:
        
        statement = select(Category).where(
            Category.id == category_id, Category.user_id == current_user.id
        )
        category = session.exec(statement).first()

        if not category:
            raise ItemNotFoundException(type='Category',item_id=category_id)
        session.delete(category)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
