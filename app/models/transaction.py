from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float, Decimal


# transaction_timestamp
# base_currency, quote_currency
# side (BUY or SELL)
# foreign_amount and/or base_amount (see input options below)
# effective_rate (snapsho 

class Transaction:
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    transaction_timestamp = Column(DateTime, index=True)
    base_currency = Column(String, index=True)
    foreign_currency = Column(String, index=True)
    base_amount = Column(Decimal, index=True)
    foreign_amount = Column(Decimal, index=True)
    effective_rate = Column(Decimal, index=True)


    