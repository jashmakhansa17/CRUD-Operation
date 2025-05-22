from fastapi import status, Response, Depends, HTTPException
from sqlmodel import select
from uuid import UUID
from typing import Annotated
from sqlalchemy.exc import IntegrityError
from ..models.category_model import Category
from ..models.user_model import User
from ..schemas.category_schema import (
    CreateCategory,
    UpdateCategory,
    NestedCategoryResponse,
)
from ..models.user_model import User
from ..core.dependencies import admin_access, SessionDep
from ..core.exceptions import (
    ItemInvalidDataException,
    InternalServerException,
    ItemNotFoundException,
    UserNotFoundException,
)


class CategoryService:
    def __init__(self, session: SessionDep, current_user: User):
        self.session = session
        self.current_user = current_user

    def create_category_for_current_admin(
        self, category: CreateCategory
    ) -> dict[str, str | int | None]:
        try:
            if category.parent_id:
                parent_product = self.session.exec(
                    select(Category).where(
                        Category.id == category.parent_id,
                        Category.user_id == self.current_user.id,
                    )
                ).first()

                if not parent_product:
                    raise ItemNotFoundException(type="Parent id")

            db_category = Category(
                **category.model_dump(), user_id=self.current_user.id
            )
            self.session.add(db_category)
            self.session.commit()
            self.session.refresh(db_category)
            return db_category

        except ItemNotFoundException:
            self.session.rollback()
            raise

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__)

    def create_category_for_user(self, user_id: UUID, category: CreateCategory):
        try:
            statement = select(User).where(User.id == user_id, User.role == "user")
            user = self.session.exec(statement).first()

            if not user:
                raise UserNotFoundException(type="User")

            if category.parent_id:
                parent_product = self.session.exec(
                    select(Category).where(
                        Category.id == category.parent_id, Category.user_id == user_id
                    )
                ).first()

                if not parent_product:
                    raise ItemNotFoundException(type="Parent id")

            db_category = Category(**category.model_dump(), user_id=user_id)
            self.session.add(db_category)
            self.session.commit()
            self.session.refresh(db_category)
            return db_category

        except UserNotFoundException:
            self.session.rollback()
            raise

        except ItemNotFoundException:
            self.session.rollback()
            raise

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__)

    def get_categories_for_current_person(self) -> list[dict[str, str | int | None]]:
        try:
            categories = self.session.exec(
                select(Category).where(Category.user_id == self.current_user.id)
            ).all()

            return categories

        except Exception as e:
            raise InternalServerException(e, __name__)

    def get_all_categories_for_admin(self) -> list[dict[str, str | int | None]]:
        try:
            categories = self.session.exec(select(Category)).all()

            return categories

        except Exception as e:
            raise InternalServerException(e, __name__)

    def get_pagination_categories(
        self,
        page: int = 1,
        size: int = 10,
        parent_id: UUID | None = None,
    ) -> list[dict[str, str | int | None]]:
        try:
            query = select(Category).where(Category.user_id == self.current_user.id)

            if parent_id is not None:
                query = query.where(Category.parent_id == parent_id)

            skip = (page - 1) * size
            query = query.offset(skip).limit(size)

            categories = self.session.exec(query).all()

            return categories

        except Exception as e:
            raise InternalServerException(e, __name__)

    # dependency for nested category
    def get_nested_categories(self, category: Category, user_id: UUID):
        if category.user_id != user_id:
            return None

        result = {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "user_id": user_id,
            "subcategories": [
                sub
                for sub in (
                    self.get_nested_categories(sub, user_id)
                    for sub in category.subcategories
                )
                if sub
            ],
        }
        return result

    def nested_category(self, category_id: UUID) -> NestedCategoryResponse:
        try:
            statement = select(Category).where(
                Category.id == category_id, Category.user_id == self.current_user.id
            )
            category = self.session.exec(statement).first()

            if not category:
                raise ItemNotFoundException(type="Category", item_id=category_id)

            return self.get_nested_categories(category, self.current_user.id)

        except ItemNotFoundException:
            raise

        except Exception as e:
            raise InternalServerException(e, __name__)

    def get_category_by_id(self, category_id: UUID) -> dict[str, str | int | None]:
        statement = select(Category).where(
            Category.id == category_id, Category.user_id == self.current_user.id
        )
        category = self.session.exec(statement).first()

        if not category:
            raise ItemNotFoundException(type="Category", item_id=category_id)
        return category

    def update_category_for_current_admin(
        self, category_id: UUID, category_update: UpdateCategory
    ) -> dict[str, str | int | None]:
        try:
            statement = select(Category).where(
                Category.id == category_id, Category.user_id == self.current_user.id
            )
            category = self.session.exec(statement).first()

            if not category:
                raise ItemNotFoundException(type="Category", item_id=category_id)

            if category.parent_id:
                parent_product = self.session.exec(
                    select(Category).where(
                        Category.id == category.parent_id,
                        Category.user_id == self.current_user.id,
                    )
                ).first()

                if not parent_product:
                    raise ItemNotFoundException(type="Parent id")

            category_data = category_update.model_dump(exclude_unset=True)
            for key, value in category_data.items():
                setattr(category, key, value)
            self.session.add(category)
            self.session.commit()
            self.session.refresh(category)
            return category

        except ItemNotFoundException:
            raise

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__)
        

    def update_category_for_user(
        self, user_id: UUID, category_id: UUID, category_update: UpdateCategory
    ) -> dict[str, str | int | None]:
        try:

            user_statement = select(User).where(
                User.id == user_id, User.role == "user"
            )
            user = self.session.exec(user_statement).first()

            if not user:
                raise UserNotFoundException(type='User')

            category_statement = select(Category).where(
                Category.id == category_id, Category.user_id == user_id
            )
            category = self.session.exec(category_statement).first()

            if not category:
                raise ItemNotFoundException(type="Category", item_id=category_id)

            if category.parent_id:
                parent_product = self.session.exec(
                    select(Category).where(
                        Category.id == category.parent_id,
                        Category.user_id == self.current_user.id,
                    )
                ).first()

                if not parent_product:
                    raise ItemNotFoundException(type="Parent id")

            category_data = category_update.model_dump(exclude_unset=True)
            for key, value in category_data.items():
                setattr(category, key, value)
            self.session.add(category)
            self.session.commit()
            self.session.refresh(category)
            return category

        except ItemNotFoundException:
            raise

        except IntegrityError as e:
            self.session.rollback()
            raise ItemInvalidDataException(e)

        except Exception as e:
            self.session.rollback()
            raise InternalServerException(e, __name__) 


    def delete_category_for_current_admin(self, category_id: UUID) -> None:
        statement = select(Category).where(
            Category.id == category_id, Category.user_id == self.current_user.id
        )
        category = self.session.exec(statement).first()

        if not category:
            raise ItemNotFoundException(type="Category", item_id=category_id)
        self.session.delete(category)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    def delete_category_for_user(self, user_id: UUID, category_id: UUID) -> None:
        user_statement = select(User).where(
            User.id == user_id, User.role == "user"
        )
        user = self.session.exec(user_statement).first()

        if not user:
            raise UserNotFoundException(type='User')

        category_statement = select(Category).where(
            Category.id == category_id, Category.user_id == user_id
        )
        category = self.session.exec(category_statement).first()

        if not category:
            raise ItemNotFoundException(type="Category", item_id=category_id)
        self.session.delete(category)
        self.session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)