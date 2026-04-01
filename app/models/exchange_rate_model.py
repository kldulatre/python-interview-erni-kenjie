from sqlalchemy import Column, Integer, String, Numeric, Date
from app.db.base_class import Base

class ExchangeRateModel(Base):
    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    rate_date = Column(Date, index=True)
    base_currency = Column(String, index=True)
    quote_currency = Column(String, index=True)
    rate = Column(Numeric, index=True)