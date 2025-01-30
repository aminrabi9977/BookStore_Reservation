from sqlalchemy import Column, Integer,Numeric, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
from datetime import datetime
from typing import List
from decimal import Decimal
from app.core.exceptions import ValidationError



class SubscriptionModel(str, enum.Enum):
    FREE = "Free"
    PLUS = "Plus"
    PREMIUM = "Premium"

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key= True , index = True)  
    user_id = Column(String , ForeignKey('usrs.id') , unique = True , nullable = False)
    subscription_model = Column(SQLAlchemyEnum(SubscriptionModel) , default = SubscriptionModel.FREE) 
    subscription_end_time = Column(DateTime(timezone = True))
    wallet_amount = Column(Numeric(10,2) , default = 0.0) 

    user = relationship('User' , backref = "customer")
    reservations = relationship("Reseevation" , back_populates = "customer")

    def __init__(self, **kwargs):
        self.validate_wallet_amount(kwargs.get('wallet_amount', 0.0))
        super().__init__(**kwargs)

    @staticmethod
    def validate_wallet_amount(amount: float):
        if amount < 0:
            raise ValidationError("Wallet amount cannot be negative")

    @staticmethod
    def validate_transaction(amount: float, current_balance: float) -> List[str]:
        errors = []
        if amount <= 0:
            errors.append("Amount must be positive")
        if amount > current_balance:
            errors.append("Insufficient balance")
        return errors

    def update_wallet_amount(self, amount: float):
        new_balance = self.wallet_amount + amount
        self.validate_wallet_amount(new_balance)
        self.wallet_amount = new_balance

    def update_subscription(self, subscription_type: SubscriptionModel, end_time: datetime):
        if not isinstance(subscription_model, SubscriptionModel):
            raise ValidationError("Invalid subscription type")
        if end_time < datetime.now():
            raise ValidationError("Subscription end time must be in the future")
        
        self.subscription_model = subscription_model
        self.subscription_end_time = end_time

    def can_reserve_books(self) -> bool:
        return self.subscription_model != SubscriptionModel.FREE

    def get_max_reservation_days(self) -> int:
        return 14 if self.subscription_model == SubscriptionModel.PREMIUM else 7

    def get_max_simultaneous_reservations(self) -> int:
        return 10 if self.subscription_model == SubscriptionModel.PREMIUM else 5