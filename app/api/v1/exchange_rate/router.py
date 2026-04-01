from typing import Any, List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.exchange_rate_schema import ExchangeRateResponse, ExchangeRateBase, ExchangeRateGet
from app.api.v1.exchange_rate.resources import ExchangeRateResource
from app.api.deps import get_db

router = APIRouter()

@router.get("/latest", response_model=ExchangeRateResponse)
def get_latest_exchange_rate(base_currency: str, quote_currency: str, db: Session = Depends(get_db)) -> ExchangeRateResponse:
    params = ExchangeRateGet(base_currency=base_currency, quote_currency=quote_currency)
    return ExchangeRateResource().get_latest_exchange_rate(db, params)

@router.delete("/{id}")
def delete_exchange_rate(id: int, db: Session = Depends(get_db)) -> ExchangeRateResponse:
    return ExchangeRateResource().delete_exchange_rate(id, db)