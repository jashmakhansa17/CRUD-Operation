from fastapi import APIRouter
from .category import router as category
from .product import router as product
from .admin import router as admin
from .users import router as users

router = APIRouter()

router.include_router(product, prefix='/product', tags=['Product'])
router.include_router(category, prefix='/category', tags=['Category'])
router.include_router(admin, tags=["admin"])
router.include_router(users)