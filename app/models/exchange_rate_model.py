from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float, Decimal

class ExchangeRateModel:
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    rate_date = Column(Date, index=True)
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    rate = Column(Decimal, index=True)