import re
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator, ConfigDict


_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_VALID_SIDES = {"BUY", "SELL"}


class TransactionCreate(BaseModel):
    """
    Schema for creating an FX transaction.
    Exactly one of foreign_amount or base_amount must be provided.
    """
    timestamp: datetime
    base_currency: str
    quote_currency: str
    side: str
    foreign_amount: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None

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

    @field_validator("foreign_amount", "base_amount")
    @classmethod
    def validate_positive_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be a positive number")
        return v

    @model_validator(mode="after")
    def exactly_one_amount(self):
        has_foreign = self.foreign_amount is not None
        has_base = self.base_amount is not None
        if has_foreign == has_base:
            raise ValueError(
                "Exactly one of 'foreign_amount' or 'base_amount' must be provided, not both or neither"
            )
        return self


class TransactionResponse(BaseModel):
    """Schema for transaction API responses."""
    transaction_id: str
    timestamp: datetime
    base_currency: str
    quote_currency: str
    side: str
    foreign_amount: Decimal
    base_amount: Decimal
    effective_rate: Decimal
    fee_amount: Decimal
    rounding_adjustment: Decimal

    model_config = ConfigDict(from_attributes=True)
