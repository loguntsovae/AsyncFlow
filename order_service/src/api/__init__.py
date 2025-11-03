from fastapi import APIRouter
from .orders import router as orders_router
from .health import router as health_router

api_router = APIRouter()
api_router.include_router(orders_router, prefix="/api")
# Mount health endpoints under /api so tests use /api/health
api_router.include_router(health_router, prefix="/api")
