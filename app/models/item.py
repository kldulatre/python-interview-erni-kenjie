from sqlalchemy import Column, Integer, String, Float
from app.db.base_class import Base

class Item(Base):
    """
    Item model.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float)
    owner_id = Column(Integer)
