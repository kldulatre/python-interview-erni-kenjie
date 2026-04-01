from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field

class TransactionBase(BaseModel):
    transaction_timestamp: Optional[datetime] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    side: Optional[str] = None
    base_amount: Optional[Decimal] = None
    foreign_amount: Optional[Decimal] = None
    effective_rate: Optional[Decimal] = None

class TransactionCreate(TransactionBase):
    transaction_timestamp: str
    base_currency: str
    quote_currency: str
    side: str
    base_amount: Decimal
    foreign_amount: Decimal
    effective_rate: Decimal

class TransactionDelete(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    id: int
    
    class Config:
        from_attributes = True

