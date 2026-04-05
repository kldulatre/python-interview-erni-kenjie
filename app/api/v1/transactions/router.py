"""
Transaction API router — endpoints for recording and querying FX transactions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.transactions.resources import TransactionResource
from app.schemas.transaction_schema import TransactionCreate, TransactionResponse

router = APIRouter()
_resource = TransactionResource()


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
