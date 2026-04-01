from typing import Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.exchange_rate_schema import ExchangeRateResponse, ExchangeRateBase
from app.api.v1.exchange_rate.resources import ExchangeRateResource
from app.api.deps import get_db

router = APIRouter()

@router.get("/", response_model=ExchangeRateResponse)
def get_latest_exchange_rate(base_currency: str, quote_currency: str, db: Session = Depends(get_db)) -> ExchangeRateResponse:
    return ExchangeRateResource().get_latest_exchange_rate(db, base_currency, quote_currency)

@router.delete("/{id}")
def delete_exchange_rate(id: int) -> ExchangeRateResponse:
    return ExchangeRateResource().delete_exchange_rate(id)