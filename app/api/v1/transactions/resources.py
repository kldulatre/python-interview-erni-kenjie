"""
Transaction resource layer — business logic for creating and querying transactions.
"""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.v1.exchange_rate.resources import ExchangeRateResource
from app.models.transaction_model import TransactionModel
from app.schemas.transaction_schema import TransactionCreate
from app.services.transaction_handler import TransactionHandlerFactory


class TransactionResource:
    """Encapsulates transaction creation and query logic."""

    def __init__(self):
        self._rate_resource = ExchangeRateResource()

    def create_transaction(self, db: Session, payload: TransactionCreate) -> TransactionModel:
        """
        Create an FX transaction:
          1. Look up the daily rate for the transaction date + currency pair + side
          2. Use the polymorphic handler to compute amounts, fees, rounding
          3. Generate a transaction ID
          4. Persist and return the record
        """
        txn_date = payload.timestamp.date()

        from app.api.v1.currency.resources import CurrencyResource
        CurrencyResource().validate_currencies(db, [payload.base_currency, payload.quote_currency])

        # 1. Rate lookup
        rate_record = self._rate_resource.get_rate(
            db,
            rate_date=txn_date,
            base_currency=payload.base_currency,
            quote_currency=payload.quote_currency,
            side=payload.side,
        )
        if rate_record is None:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"No daily rate found for {payload.base_currency}/{payload.quote_currency} "
                    f"({payload.side}) on {txn_date.isoformat()}. "
                    f"Please create a rate via POST /api/v1/rates before recording a transaction."
                ),
            )

        rate_value = Decimal(str(rate_record.rate))

        # 2. Polymorphic handler
        handler = TransactionHandlerFactory.get_handler(payload.side)
        result = handler.process(
            rate=rate_value,
            base_currency=payload.base_currency,
            foreign_amount=payload.foreign_amount,
            base_amount=payload.base_amount,
        )

        # 3. Generate transaction ID
        txn_id = handler.generate_transaction_id(db, txn_date)

        # 4. Persist
        txn = TransactionModel(
            transaction_id=txn_id,
            exchange_rate_id=rate_record.id,
            transaction_timestamp=payload.timestamp,
            base_currency=payload.base_currency,
            quote_currency=payload.quote_currency,
            side=payload.side,
            foreign_amount=result["foreign_amount"],
            base_amount=result["base_amount"],
            effective_rate=result["effective_rate"],
            fee_amount=result["fee_amount"],
            rounding_adjustment=result["rounding_adjustment"],
        )
        db.add(txn)
        try:
            db.commit()
            db.refresh(txn)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return txn

    def get_transaction_by_id(self, db: Session, transaction_id: str) -> TransactionModel:
        txn = (
            db.query(TransactionModel)
            .filter(TransactionModel.transaction_id == transaction_id, TransactionModel.is_deleted == False)
            .first()
        )
        if txn is None:
            raise HTTPException(
                status_code=404,
                detail=f"Transaction '{transaction_id}' not found",
            )
        return txn

    def list_transactions(
        self,
        db: Session,
        base_currency: str | None = None,
        quote_currency: str | None = None,
        side: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TransactionModel]:
        query = db.query(TransactionModel).filter(TransactionModel.is_deleted == False)

        if base_currency:
            query = query.filter(TransactionModel.base_currency == base_currency.upper())
        if quote_currency:
            query = query.filter(TransactionModel.quote_currency == quote_currency.upper())
        if side:
            query = query.filter(TransactionModel.side == side.upper())

        return (
            query.order_by(TransactionModel.transaction_timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete_transaction(self, db: Session, transaction_id: str) -> None:
        txn = self.get_transaction_by_id(db, transaction_id)
        txn.is_deleted = True
        try:
            db.commit()
            db.refresh(txn)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
