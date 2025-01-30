from pydantic import BaseModel, field_validator, constr
from typing import Optional
from datetime import datetime

class BookCreateRequest(BaseModel):
    title: str
    isbn: str
    price: float
    genre_id: Optional[int]
    description: Optional[str]
    total_units: int = 1

    @field_validator('title')  
    def validate_title(cls, v):  
        if not (1 <= len(v) <= 255):  
            raise ValueError("Title must be between 1 and 255 caracters")  
        return v  

    @field_validator('isbn')  
    def validate_isbn(cls, v):  
        if len(v) != 13 or not v.isdigit():  
            raise ValueError("ISBN must be a 13 number")  
        return v  

    @field_validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price must not be negative")
        return v

    @field_validator('total_units')
    def validate_units(cls, v):
        if v < 1:
            raise ValueError("Total units must be at least 1")
        return v