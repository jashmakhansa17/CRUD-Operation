from fastapi import APIRouter, Depends
from typing import Annotated
from uuid import UUID

from ..schemas.product_schema import CreateProduct, ReadProduct, UpdateProduct

from ..services.product_service import ProductService
from ..core.dependencies import get_current_user, SessionDep, admin_access
from ..models.user_model import User


def get_product_service(
    session: SessionDep, current_user: User = Depends(get_current_user)
) -> ProductService:
    return ProductService(session, current_user)


router = APIRouter()


# Create a product
@router.post(
    "/",
    summary="Create a product",
    description="Creates a new product and stores it in the database. Returns the created product.",
    response_model=ReadProduct,
)
async def create_product(
    product: CreateProduct,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> dict[str, str | int]:
    return product_service.create_product(product)


# Get all products
@router.get(
    "/",
    summary="Get all products",
    description="Retrieve a list of all products from the database.",
    response_model=list[ReadProduct],
)
async def get_products(
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> list[dict[str, str | int]]:
    return product_service.get_products()


# get all products for admin
@router.get(
    "/all",
    summary="Get all products for admin",
    description="Retrieve a list of all products from the database.",
    response_model=list[ReadProduct],
)
async def get_all_products(
    product_service: Annotated[ProductService, Depends(admin_access)],
) -> list[dict[str, str | int]]:
    return product_service.get_all_products()


# Get products after validation
@router.get(
    "/pagination",
    summary="Get all products by validating",
    description="Retrieve a list of all products from the database with validations like limit, offset, based on price and specific category.",
    response_model=list[ReadProduct],
)
async def get_pagination_products(
    product_service: Annotated[ProductService, Depends(get_product_service)],
    page: int = 1,
    size: int = 10,
    category_id: int | None = None,
    price_min: float | None = None,
    price_max: float | None = None,
) -> list[dict[str, str | int]]:
    return product_service.get_pagination_products(
        page, size, category_id, price_min, price_max
    )


# Get a product by ID
@router.get(
    "/{product_id}",
    summary="Get a product by ID",
    description="Retrieve the details of a product by its ID.",
    response_model=ReadProduct,
)
async def get_product(
    product_id: UUID,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> dict[str, str | int]:
    return product_service.get_product(product_id)


# Update a product
@router.put(
    "/{product_id}",
    summary="Update a product",
    description="Updates a product by its ID with the provided data.",
    response_model=ReadProduct,
)
async def update_product(
    product_id: UUID,
    product_update: UpdateProduct,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> dict[str, str | int]:
    return product_service.update_product(product_id, product_update)


# Delete a product
@router.delete(
    "/{product_id}",
    summary="Delete a product",
    description="Deletes a product by its ID.",
)
async def delete_product(
    product_id: UUID,
    product_service: Annotated[ProductService, Depends(get_product_service)],
) -> None:
    return product_service.delete_product(product_id)
