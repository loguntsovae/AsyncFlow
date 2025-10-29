from .orders import router as orders_router
from .health import router as health_router

api_router = APIRouter()
api_router.include_router(orders_router)
api_router.include_router(health_router)
