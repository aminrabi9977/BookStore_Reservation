from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from app.database import Base
import enum
from sqlalchemy.orm import relationship

class UserRole(str, enum.Enum):
    ADMIN: "Admin"
    AUTHOR: "Author"
    CUSTOMER: "Customer"


class User(Base):
    __tablename__ = "users"    

    id = Column(Integer , primary_key = True , index = True)
    user_name = Column(String , unique = True , index = True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String , unique = True , index = True)
    phone = Column(String)
    password = Column(String)
    role = Column(SQLAlchemyEnum(UserRole))
    author = relationship("Author", back_populates="user" , uselist = False)