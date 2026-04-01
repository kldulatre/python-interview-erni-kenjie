from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class ExchangeRateBase(BaseModel):
    rate_date: Optional[str] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    side: Optional[str] = None
    rate: Optional[Decimal] = None

class ExchangeRateCreate(ExchangeRateBase):
    pass

class ExchangeRateDelete(ExchangeRateBase):
    pass

class ExchangeRateResponse(ExchangeRateBase):
    id: int
    
    class Config:
        from_attributes = True
