from typing import Optional, List
from pydantic import BaseModel, constr,validator, Field, field_validator  
from datetime import datetime
class BookBase(BaseModel):
    title: str
    price: float
    genre_id: Optional[int]
    description: Optional[str]
    total_units: int = 1
    available_units: Optional[int] = None
    isbn: str = Field(...)  

    @field_validator('isbn')  
    def validate_isbn(cls, isbn):  
        if not isbn.isdigit() or len(isbn) != 13:  
            raise ValueError('ISBN must be a 13-digit number')  
        return isbn  
    class Config:  
       
        from_attributes = True    

class BookCreate(BookBase):
    author_ids: List[int]


class Book(BookBase):
    id: int
    
    class Config:
        # orm_mode = True
        from_attributes = True

class BookUpdate(BaseModel):
    title: Optional[str]
    price: Optional[float]
    genre_id: Optional[int]
    description: Optional[str]
    total_units: Optional[int]
    author_ids: Optional[List[int]]

class AuthorInBook(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str

    class Config:
        # orm_mode = True
        from_attributes = True

class BookResponse(BookBase):
    id: int
    authors: List[AuthorInBook]
    created_at: datetime
    updated_at: datetime

    class Config:
        # orm_mode = True    
        from_attributes = True