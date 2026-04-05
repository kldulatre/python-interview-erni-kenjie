from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.exchange_rate import router as exchange_rate_router
from app.api.v1.transactions import router as transaction_router
from app.api.v1.currency import router as currency_router

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(exchange_rate_router.router, prefix="/rates", tags=["exchange-rates"])
api_router.include_router(transaction_router.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(currency_router.router, prefix="/currencies", tags=["currencies"])
