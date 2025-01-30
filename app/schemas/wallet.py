from pydantic import BaseModel, condecimal
from typing import Optional
from decimal import Decimal


PositiveDecimal = condecimal(gt=Decimal('0'))


class WalletTransaction(BaseModel):
    amount: PositiveDecimal  
    description: Optional[str] = None

class WalletStatus(BaseModel):
    current_balance: Decimal
    pending_charges: Decimal
    available_balance: Decimal