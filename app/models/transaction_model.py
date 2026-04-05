from sqlalchemy import Column, Integer, String, Numeric, DateTime
from app.db.base_class import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    transaction_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    base_currency = Column(String(3), nullable=False, index=True)
    quote_currency = Column(String(3), nullable=False, index=True)
    side = Column(String(4), nullable=False, index=True)
    foreign_amount = Column(Numeric(precision=18, scale=6), nullable=False)
    base_amount = Column(Numeric(precision=18, scale=6), nullable=False)
    effective_rate = Column(Numeric(precision=18, scale=6), nullable=False)
    fee_amount = Column(Numeric(precision=18, scale=6), nullable=False, default=0)
    rounding_adjustment = Column(Numeric(precision=18, scale=6), nullable=False, default=0)