"""
Transaction API router — endpoints for recording and querying FX transactions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.transactions.resources import TransactionResource
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse
from app.schemas.suggestion_schema import SuggestionRequest, SuggestionResponse
from app.services.transaction_handler import TransactionHandlerFactory

router = APIRouter()
_resource = TransactionResource()

@router.post("/suggest", response_model=SuggestionResponse)
def get_rounding_suggestion(payload: SuggestionRequest, db: Session = Depends(get_db)):
    """
    Given an amount and currency pair, fetch today's rate, compute the rounding 
    adjustment required, and suggest options to the teller.
    """
    if payload.foreign_amount is None and payload.base_amount is None:
        raise HTTPException(status_code=422, detail="Either foreign_amount or base_amount is required.")
    if payload.foreign_amount is not None and payload.base_amount is not None:
        raise HTTPException(status_code=422, detail="Only one of foreign_amount or base_amount should be provided.")

    from datetime import datetime
    from app.api.v1.exchange_rate.resources import ExchangeRateResource
    from decimal import Decimal

    today = datetime.now().date()
    rate_record = ExchangeRateResource().get_rate(
        db,
        rate_date=today,
        base_currency=payload.base_currency,
        quote_currency=payload.quote_currency,
        side=payload.side,
    )
    if not rate_record:
        raise HTTPException(status_code=422, detail=f"No rate found for {payload.base_currency}/{payload.quote_currency} today.")

    rate_val = Decimal(str(rate_record.rate))

    handler = TransactionHandlerFactory.get_handler(payload.side)
    result = handler.process(
        rate=rate_val,
        foreign_amount=payload.foreign_amount,
        base_amount=payload.base_amount,
    )

    exact_total = result["base_amount"] - result["rounding_adjustment"]
    
    # Calculate the options based on the 0.05 cash step
    step = Decimal("0.05")
    remainder = exact_total % step
    if remainder == Decimal("0"):
        business_absorbs = Decimal("0.00")
        customer_adds = Decimal("0.00")
    else:
        business_absorbs = remainder
        customer_adds = step - remainder

    return SuggestionResponse(
        exact_base_total=exact_total,
        rounded_base_total=result["base_amount"],
        rounding_adjustment=result["rounding_adjustment"],
        fee_amount=result["fee_amount"],
        customer_adds=customer_adds,
        business_absorbs=business_absorbs
    )



@router.post("/", response_model=TransactionResponse, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    """
    Record an FX transaction.

    The system will:
    1. Look up the daily rate for the transaction date
    2. Apply business rules (fees, rounding) via the polymorphic handler
    3. Store and return the transaction with computed amounts
    """
    txn = _resource.create_transaction(db, payload)

    return TransactionResponse(
        transaction_id=txn.transaction_id,
        timestamp=txn.transaction_timestamp,
        base_currency=txn.base_currency,
        quote_currency=txn.quote_currency,
        side=txn.side,
        foreign_amount=txn.foreign_amount,
        base_amount=txn.base_amount,
        effective_rate=txn.effective_rate,
        fee_amount=txn.fee_amount,
        rounding_adjustment=txn.rounding_adjustment,
    )


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    base_currency: Optional[str] = Query(None),
    quote_currency: Optional[str] = Query(None),
    side: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List transactions with optional filters."""
    txns = _resource.list_transactions(db, base_currency, quote_currency, side, skip, limit)
    return [
        TransactionResponse(
            transaction_id=txn.transaction_id,
            timestamp=txn.transaction_timestamp,
            base_currency=txn.base_currency,
            quote_currency=txn.quote_currency,
            side=txn.side,
            foreign_amount=txn.foreign_amount,
            base_amount=txn.base_amount,
            effective_rate=txn.effective_rate,
            fee_amount=txn.fee_amount,
            rounding_adjustment=txn.rounding_adjustment,
        )
        for txn in txns
    ]


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve a single transaction by its transaction ID."""
    txn = _resource.get_transaction_by_id(db, transaction_id)
    return TransactionResponse(
        transaction_id=txn.transaction_id,
        timestamp=txn.transaction_timestamp,
        base_currency=txn.base_currency,
        quote_currency=txn.quote_currency,
        side=txn.side,
        foreign_amount=txn.foreign_amount,
        base_amount=txn.base_amount,
        effective_rate=txn.effective_rate,
        fee_amount=txn.fee_amount,
        rounding_adjustment=txn.rounding_adjustment,
    )
