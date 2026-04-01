from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

class CurrencyBase(BaseModel):
    code: Optional[str] = None

class CurrencyCreate(CurrencyBase):
    code: str

class CurrencyDelete(CurrencyBase):
    id: int

class CurrencyResponse(CurrencyBase):
    id: int
    
    class Config:
        from_attributes = True