
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


from app.database import Base

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id'))
    goodreads_link = Column(String)
    bank_account_number = Column(String)
    user = relationship("User", back_populates="author")
    books = relationship("Book", secondary="book_authors", back_populates="authors")
    city = relationship("City", back_populates="authors")