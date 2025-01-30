from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional
from datetime import datetime

class UserRole(str, Enum):
    ADMIN: "Admin"
    AUTHOR: "Author"
    CUSTOMER: "Customer"

class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole    

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class config:
        # orm_mode = True
        from_attributes = True
        
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    password: str


