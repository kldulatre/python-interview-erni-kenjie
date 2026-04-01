from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Float

# Local imports
# from app.db.base_class import Base

# Note: In a real project, you'd use a Base class from app.db.session.
# For now, this is a placeholder to show the structure.

class Item:
    """
    Sample Item model.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Float)
    owner_id = Column(Integer)
