from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from sql_database import Base

class Food_items(Base):
    __tablename__ = 'food_items'
    item_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    price = Column(float, nullable=False)
