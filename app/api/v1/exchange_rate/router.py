from typing import Any, List
from fastapi import APIRouter, HTTPException

from app.schemas.exchange_rate_schema import ExchangeRateCreate, ExchangeRateResponse
from app.api.v1.exchange_rate.resources import ExchangeRateResource

router = APIRouter()

@router.get("/", response_model=ExchangeRateResponse)
def get_latest_exchange_rate() -> ExchangeRateResponse:
    return ExchangeRateResource().get_latest_exchange_rate()

@router.delete("/{id}")
def delete_exchange_rate(id: int) -> ExchangeRateResponse:
    return ExchangeRateResource().delete_exchange_rate(id)