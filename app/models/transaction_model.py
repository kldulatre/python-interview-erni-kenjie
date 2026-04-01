from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.db.base_class import Base

class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    transaction_timestamp = Column(DateTime, index=True)
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    base_amount = Column(Numeric, index=True)
    foreign_amount = Column(Numeric, index=True)
    actual_rate = Column(Numeric, index=True)
    effective_rate = Column(Numeric, index=True)