from fastapi import APIRouter, Depends

from ..core.dependencies import SessionDep
from ..schemas.category_schema import CreateCategory, ReadCategory, UpdateCategory, NestedCategoryResponse
from typing import Annotated
from ..models.user_model import User
from uuid import UUID
from ..core.dependencies import admin_access, get_current_user

from ..services.category_service import CategoryService


router = APIRouter()


# Create a category
@router.post(
    "/",
    summary="Create a category",
    description="Creates a new category and stores it in the database. Returns the created category.",
    response_model=ReadCategory
)
async def create_category(category: CreateCategory, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> dict[str, str | int | None]:
    return CategoryService.create_category(category, session, current_user)


# Get all categories
@router.get(
    '/',
    summary="Get all categories",
    description="Retrieve a list of all categories from the database.",
    response_model=list[ReadCategory]
)
async def get_categories(session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> list[dict[str, str | int | None]]:
    return CategoryService.get_categories(session, current_user)


# Get categories after validation
@router.get(
    '/pagination',
    summary="Get all categories by validating",
    description="Retrieve a list of all categories from the database with validations like limit, offset and parent id.",
    response_model=list[ReadCategory]
)
async def get_validate_categories(
    session: SessionDep,
    current_user: Annotated[User,Depends(get_current_user)],
    page: int = 1, 
    size: int = 10,
    parent_id: int | None = None, 
) -> list[dict[str, str | int | None]]:
    return CategoryService.get_pagination_categories(session, current_user, page, size, parent_id)



# Get nested category
@router.get(
    '/nested/{category_id}',
    summary='Get nested category',
    description='Retrieve all the categories with their nested category',
    response_model=NestedCategoryResponse
)
async def nested_category(category_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> NestedCategoryResponse:
    return CategoryService.nested_category(category_id, session, current_user)


# Get a category by ID
@router.get(
    '/{category_id}',
    summary="Get a category by ID",
    description="Retrieve the details of a category by its ID.",
    response_model=ReadCategory
)
async def read_category(category_id: UUID, session: SessionDep, current_user: Annotated[User,Depends(get_current_user)]) -> dict[str, str | int | None]:
    return CategoryService.read_category(category_id, session, current_user)


@router.put(
    '/{category_id}',
    summary='Update a category by ID',
    description='Update the details of category, make sure you provide data that need to be update.',
    response_model=ReadCategory
)
async def update_product(category_id: UUID, category_update: UpdateCategory, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> dict[str, str | int | None]:
    return CategoryService.update_category(category_id, category_update, session, current_user)


@router.delete(
    '/{category_id}',
    summary="Delete a category",
    description="Deletes a category by its ID."
)
async def delete_product(category_id: UUID, session: SessionDep, current_user: Annotated[User, Depends(admin_access)]) -> None:
    return CategoryService.delete_category(category_id, session, current_user)

