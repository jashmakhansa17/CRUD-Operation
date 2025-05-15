from fastapi import APIRouter
from .category_route import router as category
from .product_route import router as product
from .admin_route import router as admin
from .users_route import router as users

router = APIRouter()

router.include_router(product, prefix="/product", tags=["Product"])
router.include_router(category, prefix="/category", tags=["Category"])
router.include_router(admin, tags=["admin"])
router.include_router(users)
