from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float, Decimal

class CurrenciesModel:
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)