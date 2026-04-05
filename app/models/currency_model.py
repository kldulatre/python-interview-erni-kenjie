from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class CurrencyModel(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
