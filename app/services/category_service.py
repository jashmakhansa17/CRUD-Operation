from fastapi import status, Response
from ..core.dependencies import SessionDep
from ..models.category_model import Category
from ..schemas.category_schema import CreateCategory, UpdateCategory, NestedCategoryResponse
from sqlmodel import select
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from ..core.exceptions import ItemInvalidDataException, InternalServerException, ItemNotFoundException
 

class CategoryService:

    @staticmethod
    def create_category(category: CreateCategory, session: SessionDep) -> dict[str, str | int | None]:
        try:
            db_category = Category(**category.model_dump())
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
    def get_categories(session: SessionDep) -> list[dict[str, str | int | None]]:
        try:
            categories = session.exec(select(Category)).all()
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
    page: int = 1, 
    size: int = 10,
    parent_id: UUID | None = None, 
    ) -> list[dict[str, str | int | None]]:
        try:
            query = select(Category)

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
    def get_nested_categories(category: Category):
        result = {
            'id':category.id,
            'name':category.name,
            'patent_id':category.parent_id,
            'subcategories' : [
                CategoryService.get_nested_categories(sub) for sub in category.subcategories
            ]
        }
        return result
    

    @staticmethod
    def nested_category(category_id: UUID, session: SessionDep) -> NestedCategoryResponse:
        try:
            category = session.get(Category,category_id)
            if not category:
                raise ItemNotFoundException(type='Category', item_id=category_id)
            return CategoryService.get_nested_categories(category)
        
        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)
        

    @staticmethod
    def read_category(category_id: UUID, session: SessionDep) -> dict[str, str | int | None]:
        category = session.get(Category, category_id)
        if not category:
            raise ItemNotFoundException(type='Category', item_id=category_id)
        return category
    

    @staticmethod
    def update_category(category_id: UUID, category_update: UpdateCategory, session: SessionDep) -> dict[str, str | int | None]:
        try:
            category = session.get(Category, category_id)
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
    def delete_category(category_id: UUID, session: SessionDep) -> None:
        category = session.get(Category, category_id)
        if not category:
            raise ItemNotFoundException(type='Category',item_id=category_id)
        session.delete(category)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
