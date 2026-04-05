"""
Exchange Rate API router — Full CRUD for daily exchange rates.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.exchange_rate.resources import ExchangeRateResource
from app.schemas.exchange_rate_schema import (
    ExchangeRateCreate,
    ExchangeRateResponse,
    ExchangeRateUpdate,
)

router = APIRouter()
_resource = ExchangeRateResource()


@router.post("/", response_model=ExchangeRateResponse, status_code=201)
def create_rate(
    payload: ExchangeRateCreate,
    db: Session = Depends(get_db),
):
    """Create or upsert a daily exchange rate."""
    return _resource.create_or_update_rate(db, payload)


@router.get("/", response_model=List[ExchangeRateResponse])
def list_rates(
    rate_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    base_currency: Optional[str] = Query(None, description="Filter by base currency (e.g. PHP)"),
    quote_currency: Optional[str] = Query(None, description="Filter by quote currency (e.g. USD)"),
    side: Optional[str] = Query(None, description="Filter by side (BUY or SELL)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List exchange rates with optional filters."""
    return _resource.list_rates(db, rate_date, base_currency, quote_currency, side, skip, limit)


@router.get("/{rate_id}", response_model=ExchangeRateResponse)
def get_rate(
    rate_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a single exchange rate by ID."""
    return _resource.get_rate_by_id(db, rate_id)


@router.put("/{rate_id}", response_model=ExchangeRateResponse)
def update_rate(
    rate_id: int,
    payload: ExchangeRateUpdate,
    db: Session = Depends(get_db),
):
    """Update the rate value of an existing daily rate."""
    return _resource.update_rate(db, rate_id, payload)


@router.delete("/{rate_id}", response_model=ExchangeRateResponse)
def delete_rate(
    rate_id: int,
    db: Session = Depends(get_db),
):
    """Delete an exchange rate by ID."""
    return _resource.delete_rate(db, rate_id)