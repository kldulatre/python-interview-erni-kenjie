from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemas.transaction_schema import _VALID_SIDES

class SuggestionRequest(BaseModel):
    """
    Payload for requesting a rounding suggestion.
    Either foreign_amount or base_amount must be provided.
    """
    side: str
    base_currency: str
    quote_currency: str
    foreign_amount: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None

    @field_validator("base_currency", "quote_currency")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        import re
        v = v.upper().strip()
        if not re.match(r"^[A-Z]{3}$", v):
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
    def validate_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Value must be a positive number")
        return v

class SuggestionResponse(BaseModel):
    """
    Response providing the calculation breakdown and a business suggestion.
    """
    exact_base_total: Decimal
    rounded_base_total: Decimal
    rounding_adjustment: Decimal
    fee_amount: Decimal
    suggestion: str
