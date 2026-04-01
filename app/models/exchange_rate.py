from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float, Decimal

# Each rate has:
# rate_date (date)
# base_currency (e.g., PHP)
# quote_currency (e.g., USD)
# side (BUY or SELL)
# rate (decimal)

class ExchangeRate:
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    rate_date = Column(Date, index=True)
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    rate = Column(Decimal, index=True)