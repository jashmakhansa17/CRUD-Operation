from fastapi import APIRouter, Depends
from typing import Annotated
from uuid import UUID

from ..schemas.category_schema import (
    CreateCategory,
    ReadCategory,
    UpdateCategory,
    NestedCategoryResponse,
)
from ..models.user_model import User
from ..core.dependencies import admin_access, get_current_user, SessionDep

from ..services.category_service import CategoryService


def get_category_service_admin(
    session: SessionDep, current_user: User = Depends(admin_access)
) -> CategoryService:
    return CategoryService(session, current_user)


def get_category_service_all(
    session: SessionDep, current_user: User = Depends(get_current_user)
) -> CategoryService:
    return CategoryService(session, current_user)


router = APIRouter()


# Create a category
@router.post(
    "/",
    summary="Create a category for current admin",
    description="Creates a new category and stores it in the database for current person. Returns the created category.",
    response_model=ReadCategory,
)
async def create_category_for_current_admin(
    category: CreateCategory,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> dict[str, str | int | None]:
    return category_service.create_category_for_current_admin(category)


# create a category for user
@router.post(
    "/user",
    summary="Create a category for user",
    description="Creates a new category for user and stores it in the database. Returns the created category.",
)
async def create_category_for_user(
    user_id: UUID,
    category: CreateCategory,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
):
    return category_service.create_category_for_user(user_id, category)


# Get categories for current person
@router.get(
    "/",
    summary="Get categories for current person",
    description="Retrieve a list of all categories from the database for current person.",
    response_model=list[ReadCategory],
)
async def get_categories_for_current_person(
    category_service: Annotated[CategoryService, Depends(get_category_service_all)],
) -> list[dict[str, str | int | None]]:
    return category_service.get_categories_for_current_person()


# Get all categories for admin
@router.get(
    "/all",
    summary="Get all categories for admin",
    description="Retrieve a list of all categories of all users from the database.",
    response_model=list[ReadCategory],
)
async def get_all_categories_for_admin(
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> list[dict[str, str | int | None]]:
    return category_service.get_all_categories_for_admin()


# Get categories after pagination
@router.get(
    "/pagination",
    summary="Get all categories by validating",
    description="Retrieve a list of all categories from the database with validations like limit, offset and parent id.",
    response_model=list[ReadCategory],
)
async def get_pagination_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service_all)],
    page: int = 1,
    size: int = 10,
    parent_id: int | None  = None,
) -> list[dict[str, str | int | None]]:
    return category_service.get_pagination_categories(page, size, parent_id)


# Get nested category
@router.get(
    "/nested/{category_id}",
    summary="Get nested category",
    description="Retrieve all the categories with their nested category",
    response_model=NestedCategoryResponse,
)
async def nested_category(
    category_id: UUID,
    category_service: Annotated[CategoryService, Depends(get_category_service_all)],
) -> NestedCategoryResponse:
    return category_service.nested_category(category_id)


# Get a category by ID
@router.get(
    "/{category_id}",
    summary="Get a category by ID",
    description="Retrieve the details of a category by its ID.",
    response_model=ReadCategory,
)
async def get_category_by_id(
    category_id: UUID,
    category_service: Annotated[CategoryService, Depends(get_category_service_all)],
) -> dict[str, str | int | None]:
    return category_service.get_category_by_id(category_id)


@router.put(
    "/{category_id}",
    summary="Update a category for current admin by ID",
    description="Update the details of category for current admin, make sure you provide data that need to be update.",
    response_model=ReadCategory,
)
async def update_category_for_current_admin(
    category_id: UUID,
    category_update: UpdateCategory,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> dict[str, str | int | None]:
    return category_service.update_category_for_current_admin(category_id, category_update)


@router.put(
    "/user/{user_id}",
    summary="Update a category for user by ID",
    description="Update the details of category for user, make sure you provide data that need to be update.",
    response_model=ReadCategory,
)
async def update_category_for_user(
    category_id: UUID,
    user_id: UUID,
    category_update: UpdateCategory,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> dict[str, str | int | None]:
    return category_service.update_category_for_user(user_id, category_id, category_update)


@router.delete(
    "/{category_id}",
    summary="Delete a category for a current admin",
    description="Deletes a category for admin by its ID.",
)
async def delete_category_for_current_admin(
    category_id: UUID,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> None:
    return category_service.delete_category_for_current_admin(category_id)


@router.delete(
    '/user/{user_id}',
    summary='Delete a category for user',
    description='Deletes a category for user by its ID.'
)
async def delete_category_for_user(
    category_id: UUID,
    user_id: UUID,
    category_service: Annotated[CategoryService, Depends(get_category_service_admin)],
) -> None:
    return category_service.delete_category_for_user(user_id, category_id)