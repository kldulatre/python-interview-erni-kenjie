from sqlalchemy import Column, Integer, String, Numeric, Date, UniqueConstraint
from app.db.base_class import Base


class ExchangeRateModel(Base):
    __tablename__ = "exchange_rates"

    __table_args__ = (
        UniqueConstraint(
            "rate_date", "base_currency", "quote_currency", "side",
            name="uq_rate_date_currency_side"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    rate_date = Column(Date, nullable=False, index=True)
    base_currency = Column(String(3), nullable=False, index=True)
    quote_currency = Column(String(3), nullable=False, index=True)
    side = Column(String(4), nullable=False, index=True)
    rate = Column(Numeric(precision=18, scale=6), nullable=False)