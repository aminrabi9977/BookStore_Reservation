from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Tuple
from decimal import Decimal

from app.models.reservation import Reservation, ReservationStatus
from app.models.customer import Customer, SubscriptionModel
from app.models.book import Book
from app.services.book_service import BookService
from app.services.queue_manager import QueueManager
from app.services.wallet_manager import WalletManager

class ReservationService:
    @staticmethod
    async def check_availability(book_id: int, db: AsyncSession) -> bool:
        query = select(Book).where(Book.id == book_id)
        result = await db.execute(query)
        book = result.scalar_one_or_none()
        return book is not None and book.available_units > 0

    @staticmethod
    async def check_user_limits(customer: Customer, db: AsyncSession) -> bool:
        active_reservations = await ReservationService.get_active_reservations_count(
            customer.id, db
        )
        max_allowed = 10 if customer.subscription_model == SubscriptionModel.PREMIUM else 5
        return active_reservations < max_allowed

    @staticmethod
    async def validate_reservation_period(customer: Customer,
        start_time: datetime,
        end_time: datetime) -> bool:
        max_days = 14 if customer.subscription_model == SubscriptionModal.PREMIUM else 7
        duration = (end_time - start_time).days
        return duration <= max_days

    @staticmethod
    async def get_reservation(reservation_id: int,
        customer_id: int,
        db: AsyncSession) -> Optional[Reservation]:
        query = select(Reservation).where(
            and_(Reservation.id == reservation_id,Reservation.customer_id == customer_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_reservations_count(customer_id: int,db: AsyncSession) -> int:
        query = select(Reservation).where(
            and_(Reservation.customer_id == customer_id,Reservation.status.in_([ReservationStatus.ACTIVE,
                    ReservationStatus.PENDING
                ])
            )
        )
        result = await db.execute(query)
        return len(result.scalars().all())

    @staticmethod
    async def validate_wallet_amount(customer: Customer,days: int,
        db: AsyncSession) -> Tuple[bool, Decimal]:
        daily_rate = Decimal('1000')  
        total_cost = days * daily_rate
    
        total_cost = await WalletManager.calculate_discounted_price(customer,total_cost,db
        )
        
        return customer.wallet_balance >= total_cost, total_cost

    @staticmethod
    async def create_instant_reservation(
        customer: Customer,
        book_id: int,
        start_time: datetime,
        end_time: datetime,
        price: Decimal,
        db: AsyncSession
    ) -> Optional[Reservation]:


        # Validate kardan hame sharayet
        if not await ReservationService.check_availability(book_id,db):
            return None
            
        if not await ReservationService.check_user_limits(customer,db):
            return None
            
        if not await ReservationService.validate_reservation_period(customer, start_time, end_time):
            return None

        # kasr az kife pool
        customer.wallet_amount -= price
        
        # ejad reservation
        reservation = Reservation(
            customer_id=customer.id,
            book_id=book_id,
            start_time=start_time,
            end_time=end_time,
            price=price,
            status=ReservationStatus.ACTIVE
        )
        
        # Update datresi be book
        await BookService.update_available_units(db, book_id, -1)
        
        db.add(reservation)
        await db.commit()
        await db.refresh(reservation)
        return reservation

    @staticmethod
    async def process_queue_reservation(
        book_id: int,
        db: AsyncSession
    ) -> None:
        queue = await QueueManager().get_queue(book_id)
        
        for reservation in queue:
            customer = await CustomerService.get_customer(reservation.customer_id, db)
            
            # Check mahdodiat reserv
            if not await ReservationService.validate_reservation_limits(customer, db):
                await QueueManager().remove_from_queue(book_id, reservation.id)
                continue
            
            # Validate kardan kife pool
            days = (reservation.end_time - reservation.start_time).days
            is_valid, cost = await ReservationService.validate_wallet_amount(customer, days,db)
            
            if not is_valid:
                await QueueManager().remove_from_queue(book_id, reservation.id)
                continue
            
            # pardazesh reserv
            success = await ReservationService.create_instant_reservation(customer,
                book_id,reservation.start_time,
                reservation.end_time,
                cost,
                db
            )
            
            if success:
                break

    # modiriate Queue 
    @staticmethod
    async def get_customer_queue_status(
        customer_id: int,
        db: AsyncSession) -> List[Reservation]:
        query = select(Reservation).where(
            and_(Reservation.customer_id == customer_id,Reservation.status == ReservationStatus.IN_QUEUE
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def exit_queue(reservation_id: int,
        customer_id: int,
        db: AsyncSession) -> bool:
        reservation = await ReservationService.get_reservation(
            reservation_id,
            customer_id,
            db
        )
        
        if not reservation or reservation.status != ReservationStatus.IN_QUEUE:
            return False
            
        reservation.status = ReservationStatus.QUEUE_CANCELLED
        await QueueManager().remove_from_queue(
            book_id=reservation.book_id,
            reservation_id=reservation.id
        )
        await db.commit()
        return True