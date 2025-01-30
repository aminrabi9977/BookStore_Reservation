
from fastapi import HTTPException, status
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.customer import Customer, SubscriptionModel


from decimal import Decimal

class PurchasingService:
    SUBSCRIPTION_PRICES = {
        SubscriptionModel.PLUS: Decimal('50000'),  
        SubscriptionModel.PREMIUM: Decimal('200000')  
    }

    @staticmethod
    async def purchase_subscription(
        customer: Customer,
        subscription_model: SubscriptionModel,
        months: int,
        db: AsyncSession
    ) -> Customer:
        if subscription_model == SubscriptionModel.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot purchase FREE subscription"
            )

        total_price = PurchasingService.SUBSCRIPTION_PRICES[subscription_model] * months
        
        if customer.wallet_amount < total_price:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient funds. Required: {total_price} Toman"
            )

        customer.wallet_amount -= total_price
        customer.subscription_model = subscription_model
        customer.subscription_end_time = (
            datetime.now() + timedelta(days=30 * months)
        )

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def charge_wallet(
        customer: Customer,
        amount: Decimal,
        db: AsyncSession
    ) -> Customer:
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be positive"
            )

        customer.wallet_amount += amount
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def process_reservation_payment(
        customer: Customer,
        amount: Decimal,
        db: AsyncSession
    ) -> bool:
        if customer.wallet_amount < amount:
            return False

        customer.wallet_amount -= amount
        await db.commit()
        return True