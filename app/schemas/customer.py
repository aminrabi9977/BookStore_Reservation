from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SubscriptionModel(str, Enum):
    FREE = "Free"
    PLUS = "Plus"
    PREMIUM = "Premium"


class CustomerBase(BaseModel):
    user_id : int
    subscription_model : SubscriptionModel = SubscriptionModel.FREE 
    subscription_end_time: Optional[datetime] 
    wallet_amount: float = 0.0

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    subscription_model : Optional[SubscriptionModel]
    subscription_end_time: Optional[datetime]
    wallet_amount: Optional[float]

class   Customer(CustomerBase):
    id: int

    class Config:
        from_attributes = True    

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class UserInfo(BaseModel):
        id: int
        username: str
        email: str
        first_name: str
        last_name: str

        class Config:
            # orm_mode = True
            from_attributes = True

    user: UserInfo

    class Config:
        # orm_mode = True
        from_attributes = True