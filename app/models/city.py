from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    authors = relationship("Author", back_populates="city")