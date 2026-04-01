from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.api.v1.exchange_rate.router import router as exchange_rate_router

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(exchange_rate_router, prefix="/exchange_rate", tags=["exchange_rate"])
