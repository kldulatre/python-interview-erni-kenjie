import re
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_VALID_SIDES = {"BUY", "SELL"}


class ExchangeRateCreate(BaseModel):
    """Schema for creating / upserting a daily exchange rate."""
    rate_date: date
    base_currency: str
    quote_currency: str
    side: str
    rate: Decimal

    @field_validator("base_currency", "quote_currency")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not _CURRENCY_RE.match(v):
            raise ValueError(f"Currency code must be a 3-letter ISO code, got '{v}'")
        return v

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        v = v.upper().strip()
        if v not in _VALID_SIDES:
            raise ValueError(f"Side must be BUY or SELL, got '{v}'")
        return v

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Rate must be a positive number")
        return v


class ExchangeRateUpdate(BaseModel):
    """Schema for updating an existing daily exchange rate."""
    rate: Decimal

    @field_validator("rate")
    @classmethod
    def validate_rate(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Rate must be a positive number")
        return v


class ExchangeRateResponse(BaseModel):
    """Schema for exchange rate API responses."""
    id: int
    rate_date: date
    base_currency: str
    quote_currency: str
    side: str
    rate: Decimal

    class Config:
        from_attributes = True


class ExchangeRateFilter(BaseModel):
    """Optional query filters for listing exchange rates."""
    rate_date: Optional[date] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    side: Optional[str] = None
