from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from app.models.reservation import Reservation, ReservationStatus
from app.models.customer import Customer, SubscriptionModel

class WalletManager:
    @staticmethod
    async def calculate_discounted_price(
        customer: Customer,
        base_price: Decimal,
        db: AsyncSession
    ) -> Decimal:
        if customer.subscription_model == SubscriptionModel.FREE:
            return base_price

        # Check kardan  baraye bishtar az 3 books khandan to mahe ghabl 
        month_ago = datetime.now() - timedelta(days=30)
        completed_query = select(Reservation).where(
            and_(
                Reservation.customer_id == customer.id,
                Reservation.status == ReservationStatus.COMPLETED,
                Reservation.end_time > month_ago
            )
        )
        result = await db.execute(completed_query)
        if len(result.scalars().all()) >= 3:
            #takhfif 30 darsad
            base_price *= Decimal('0.7')  

        # Check kardan hazinehaye bala dar 2 mahe habl 
        two_months_ago = datetime.now() - timedelta(days=60)
        spending_query = select(Reservation).where(
            and_(
                Reservation.customer_id == customer.id,
                Reservation.status == ReservationStatus.COMPLETED,
                Reservation.end_time > two_months_ago
            )
        )
        result = await db.execute(spending_query)
        total_spent = sum(r.price for r in result.scalars().all())
        if total_spent >= 300000:  
            return Decimal('0')

        return base_price

    @staticmethod
    async def has_sufficient_balance(customer: Customer,
        amount: Decimal) -> bool:
        return customer.wallet_amount >= amount

    @staticmethod
    async def process_payment(customer: Customer,
        amount: Decimal,
        db: AsyncSession) -> bool:
        if not await WalletManager.has_sufficient_balance(customer, amount):
            return False
            
        customer.wallet_amount -= amount
        await db.commit()
        return True