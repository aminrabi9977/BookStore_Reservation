
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import List

from app.models.user import User
from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.auth import get_current_user, get_current_customer

router = APIRouter(prefix="/customers", tags=["customers"])

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate,db: AsyncSession = Depends(get_db),current_user: User = Depends(get_current_user)
):
   
    query = select(Customer).where(Customer.user_id == current_user.id)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer profile already exists for this user"
        )
    
    db_customer = Customer(
        user_id=current_user.id,
        subscription_type=customer.subscription_type,
        subscription_end_time=customer.subscription_end_time,
        wallet_balance=customer.wallet_amount
    )
    
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer

@router.post("/charge-wallet", response_model=CustomerResponse)
async def charge_wallet(
    amount: float,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)):
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )
    
    current_customer.wallet_amount += amount
    await db.commit()
    await db.refresh(current_customer)
    return current_customer