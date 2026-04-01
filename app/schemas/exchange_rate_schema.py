from datetime import date
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class ExchangeRateBase(BaseModel):
    rate_date: Optional[date] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    side: Optional[str] = None
    rate: Optional[Decimal] = None

class ExchangeRateGet(ExchangeRateBase):
    base_currency: str
    quote_currency: str

class ExchangeRateDelete(ExchangeRateBase):
    pass

class ExchangeRateResponse(ExchangeRateBase):
    id: int
    
    class Config:
        from_attributes = True
