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
        """
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

        if existing:
            existing.rate = payload.rate
            db.commit()
            db.refresh(existing)
            return existing

        new_rate = ExchangeRateModel(
            rate_date=payload.rate_date,
            base_currency=payload.base_currency,
            quote_currency=payload.quote_currency,
            side=payload.side,
            rate=payload.rate,
        )
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
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
        db.commit()
        db.refresh(rate)
        return rate

    # ---------- DELETE ----------
    def delete_rate(self, db: Session, rate_id: int) -> ExchangeRateModel:
        rate = self.get_rate_by_id(db, rate_id)
        db.delete(rate)
        db.commit()
        return rate