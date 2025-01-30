
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

from app.models.customer import SubscriptionModel

class SubscriptionPurchaseRequest(BaseModel):
    subscription_model: SubscriptionModel
    months: int = 1

class WalletChargeRequest(BaseModel):
    amount: Decimal

class WalletAmountResponse(BaseModel):
    amount: Decimal