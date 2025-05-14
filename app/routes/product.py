from fastapi import APIRouter

from ..core.dependencies import SessionDep
from ..schemas.product_schema import CreateProduct, ReadProduct, UpdateProduct

from uuid import UUID

from ..services.product_service import ProductService


router = APIRouter()


# Create a product
@router.post(
    "/",
    summary="Create a product",
    description="Creates a new product and stores it in the database. Returns the created product.",
    response_model=ReadProduct
)
async def create_product(product: CreateProduct, session: SessionDep) -> dict[str, str|int]:
    return ProductService.create_product(product, session)
    

# Get all products
@router.get(
    '/',
    summary="Get all products",
    description="Retrieve a list of all products from the database.",
    response_model=list[ReadProduct]
)
async def get_products(session: SessionDep) -> list[dict[str, str|int]]:
    return ProductService.get_products(session)


# Get products after validation
@router.get(
    '/pagination',
    summary="Get all products by validating",
    description="Retrieve a list of all products from the database with validations like limit, offset, based on price and specific category.",
    response_model=list[ReadProduct]
)
async def get_validate_products(
    session: SessionDep,
    page: int = 1, 
    size: int = 10,
    category_id: int | None = None, 
    price_min: float | None = None, 
    price_max: float | None = None, 
) -> list[dict[str, str|int]]:
    return ProductService.get_pagination_products(session, page, size, category_id, price_min, price_max)


# Get a product by ID
@router.get(
    '/{product_id}',
    summary="Get a product by ID",
    description="Retrieve the details of a product by its ID.",
    response_model=ReadProduct
)
async def get_product(product_id: UUID, session: SessionDep) -> dict[str, str|int]:
    return ProductService.get_product(product_id, session)



# Update a product
@router.put(
    '/{product_id}',
    summary="Update a product",
    description="Updates a product by its ID with the provided data.",
    response_model=ReadProduct 
)
async def update_product(product_id: UUID, product_update: UpdateProduct, session: SessionDep) -> dict[str, str|int]:
    return ProductService.update_product(product_id, product_update, session)


# Delete a product
@router.delete(
    "/{product_id}",
    summary="Delete a product",
    description="Deletes a product by its ID."
)
async def delete_product(product_id: UUID, session: SessionDep) -> None:
    return ProductService.delete_product(product_id, session)