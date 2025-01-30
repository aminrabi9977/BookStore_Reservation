from app.database import Base
from sqlalchemy import Column, Integer, Numeric, Text, Integer, Table, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.exceptions import ValidationError
from decimal import Decimal



book_authors = Table(
    'book_authors', Base.metadata, 
    Column('book_id' , Integer , ForeignKey('books.id'), primary_key = True),
    Column('authors_id' , Integer , ForeignKey('authors.id'), primary_key = True)
)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer , primary_key = True , index = True)
    title = Column(String(255) , nullable = False)
    isbn  = Column(String(13) , nullable = False , unique = True , index = True)
    price = Column(Numeric(10,2) , nullable = False)
    genre_id = Column(Integer, ForeignKey('genres.id'))
    description = Column(Text)
    total_units = Column(Integer , nullable =  False , default = 1)
    available_units = Column(Integer, nullable = False , default = 1)
    authors = relationship("Author", secondary = book_authors, backref = "books")
    reservations = relationship("Reservation", back_populates="book")
    genre = relationship("Genre", back_populates="books")

    def __init__(self, **kwargs):
        self.validate_isbn(kwargs.get('isbn'))
        self.validate_price(kwargs.get('price'))
        self.validate_units(kwargs.get('total_units', 1))
        super().__init__(**kwargs)

    @staticmethod
    def validate_isbn(isbn: str):
        if not isbn or len(isbn) != 13 or not isbn.isdigit():
            raise ValidationError("ISBN must be 13 digits")

    @staticmethod
    def validate_price(price: float):
        if price is None or price < 0:
            raise ValidationError("Price must be non-negative")

    @staticmethod
    def validate_units(units: int):
        if units is None or units < 0:
            raise ValidationError("Units must be non-negative")

    def update(self, **kwargs):
        if 'isbn' in kwargs:
            self.validate_isbn(kwargs['isbn'])
            self.isbn = kwargs['isbn']
        
        if 'price' in kwargs:
            self.validate_price(kwargs['price'])
            self.price = kwargs['price']
            
        if 'total_units' in kwargs:
            self.validate_units(kwargs['total_units'])
            self.total_units = kwargs['total_units']
            
        if 'title' in kwargs:
            self.title = kwargs['title']
            
        if 'description' in kwargs:
            self.description = kwargs['description']
            
        if 'genre_id' in kwargs:
            self.genre_id = kwargs['genre_id']

    def adjust_available_units(self, change: int):
        new_available = self.available_units + change
        if new_available < 0:
            raise ValidationError("Cannot reduce available units below 0")
        if new_available > self.total_units:
            raise ValidationError("Available units cannot exceed total units")
        self.available_units = new_available