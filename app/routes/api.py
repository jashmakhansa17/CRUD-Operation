from fastapi import APIRouter
from .category import router as category
from .product import router as product

router = APIRouter()

router.include_router(product, prefix='/product', tags=['Product'])
router.include_router(category, prefix='/category', tags=['Category'])