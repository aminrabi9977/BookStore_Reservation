from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from decimal import Decimal

from app.database import get_db
from app.models.customer import Customer, SubscriptionModel
from app.schemas.purchasing import (
    SubscriptionPurchaseRequest,
    WalletChargeRequest,
    WalletAmountResponse
)
from app.core.auth import get_current_customer
from app.services.purchasing_service import PurchasingService

router = APIRouter(prefix="/purchasing", tags=["purchasing"])

@router.post("/subscription")
async def purchase_subscription(
    request: SubscriptionPurchaseRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    updated_customer = await PurchasingService.purchase_subscription(
        customer=current_customer,
        subscription_type=request.subscription_model,
        months=request.months,
        db=db
    )
    return {"message": "Subscription purchased successfully"}

@router.post("/wallet/charge")
async def charge_wallet(
    request: WalletChargeRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    updated_customer = await PurchasingService.charge_wallet(
        customer=current_customer,
        amount=request.amount,
        db=db
    )
    return {"message": "Wallet charged successfully"}

@router.get("/wallet/amount", response_model=WalletAmountResponse)
async def get_wallet_amount(
    current_customer: Customer = Depends(get_current_customer)
):
    return {"amount": current_customer.wallet_amount}