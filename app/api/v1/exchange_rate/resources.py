"""
Exchange Rate resource layer — CRUD operations against the database.
"""

from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.exchange_rate_model import ExchangeRateModel
from app.schemas.exchange_rate_schema import ExchangeRateCreate, ExchangeRateUpdate


class ExchangeRateResource:
    """Encapsulates all exchange-rate DB operations."""

    # ---------- CREATE / UPSERT ----------
    def create_or_update_rate(self, db: Session, payload: ExchangeRateCreate) -> ExchangeRateModel:
        """
        Insert a new daily rate or update the rate value if one already exists
        for the same (rate_date, base_currency, quote_currency, side).
        If payload.rate is not provided, fetch it from a 3rd party API and apply a spread.
        """
        from app.api.v1.currency.resources import CurrencyResource
        CurrencyResource().validate_currencies(db, [payload.base_currency, payload.quote_currency])

        existing = (
            db.query(ExchangeRateModel)
            .filter(
                ExchangeRateModel.rate_date == payload.rate_date,
                ExchangeRateModel.base_currency == payload.base_currency,
                ExchangeRateModel.quote_currency == payload.quote_currency,
                ExchangeRateModel.side == payload.side,
            )
            .first()
        )

        # Determine the rate to use
        final_rate = payload.rate
        if final_rate is None:
            # Fetch from 3rd party API
            from app.services.frankfurter_service import FrankfurterService
            from decimal import Decimal
            
            fetched_rate = FrankfurterService().fetch_rate(
                rate_date=payload.rate_date,
                base_currency=payload.base_currency,
                quote_currency=payload.quote_currency
            )
            
            # Apply simulated spread depending on side
            # (In reality, spread implies store makes a profit. 
            #  We simulate: SELL is 1% higher, BUY is 1% lower than market rate)
            if payload.side.upper() == "SELL":
                final_rate = fetched_rate * Decimal("1.01")
            else:
                final_rate = fetched_rate * Decimal("0.99")

            # Validate the calculated rate is positive
            if final_rate <= 0:
                 raise HTTPException(status_code=400, detail="Calculated rate is not positive")
        else:
            if final_rate <= 0:
                 raise HTTPException(status_code=400, detail="Provided rate must be a positive number")

        if existing:
            existing.rate = final_rate
            try:
                db.commit()
                db.refresh(existing)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=500, detail=str(e))
            return existing

        new_rate = ExchangeRateModel(
            rate_date=payload.rate_date,
            base_currency=payload.base_currency,
            quote_currency=payload.quote_currency,
            side=payload.side,
            rate=final_rate,
        )
        db.add(new_rate)
        try:
            db.commit()
            db.refresh(new_rate)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return new_rate

    # ---------- READ ----------
    def get_rate_by_id(self, db: Session, rate_id: int) -> ExchangeRateModel:
        rate = db.query(ExchangeRateModel).filter(ExchangeRateModel.id == rate_id).first()
        if rate is None:
            raise HTTPException(status_code=404, detail=f"Exchange rate with id={rate_id} not found")
        return rate

    def get_rate(
        self,
        db: Session,
        rate_date: date,
        base_currency: str,
        quote_currency: str,
        side: str,
    ) -> ExchangeRateModel | None:
        """Look up a specific daily rate. Returns None if not found."""
        return (
            db.query(ExchangeRateModel)
            .filter(
                ExchangeRateModel.rate_date == rate_date,
                ExchangeRateModel.base_currency == base_currency,
                ExchangeRateModel.quote_currency == quote_currency,
                ExchangeRateModel.side == side,
            )
            .first()
        )

    def list_rates(
        self,
        db: Session,
        rate_date: Optional[date] = None,
        base_currency: Optional[str] = None,
        quote_currency: Optional[str] = None,
        side: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExchangeRateModel]:
        """Return rates, optionally filtered."""
        query = db.query(ExchangeRateModel)

        if rate_date is not None:
            query = query.filter(ExchangeRateModel.rate_date == rate_date)
        if base_currency is not None:
            query = query.filter(ExchangeRateModel.base_currency == base_currency.upper())
        if quote_currency is not None:
            query = query.filter(ExchangeRateModel.quote_currency == quote_currency.upper())
        if side is not None:
            query = query.filter(ExchangeRateModel.side == side.upper())

        return query.order_by(ExchangeRateModel.rate_date.desc()).offset(skip).limit(limit).all()

    # ---------- UPDATE ----------
    def update_rate(self, db: Session, rate_id: int, payload: ExchangeRateUpdate) -> ExchangeRateModel:
        rate = self.get_rate_by_id(db, rate_id)
        rate.rate = payload.rate
        try:
            db.commit()
            db.refresh(rate)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return rate

    # ---------- DELETE ----------
    def delete_rate(self, db: Session, rate_id: int) -> ExchangeRateModel:
        rate = self.get_rate_by_id(db, rate_id)
        db.delete(rate)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        return rate