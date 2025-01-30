from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime

from app.models.user import User
from app.models.reservation import Reservation, ReservationStatus
from app.models.book import Book
from app.core.auth import SecurityService

class AdminService:
    @staticmethod
    async def revoke_user_token(admin: User,
        target_user_id: int,
        db: AsyncSession) -> bool:
        
        target = await db.get(User, target_user_id)
        if not target or target.role == "admin":
            return False
            
        await SecurityService.blacklist_user_token(target_user_id)
        return True

    @staticmethod
    async def end_reservation_early(reservation_id: int,db: AsyncSession) -> bool:
        reservation = await db.get(Reservation, reservation_id)
        if not reservation or reservation.status != ReservationStatus.ACTIVE:
            return False

        reservation.status = ReservationStatus.ENDED_EARLY
        reservation.end_time = datetime.now()
    
        book = await db.get(Book, reservation.book_id)
        if book:
            book.available_units += 1
            
        await db.commit()
        return True

    @staticmethod
    async def get_book_reservations(book_id: int,
        db: AsyncSession) -> dict:
        active_query = select(Reservation).where(
            and_(Reservation.book_id == book_id,Reservation.status == ReservationStatus.ACTIVE
            )
        )
        active_result = await db.execute(active_query)
        current_holders = active_result.scalars().all()

        queue_query = select(Reservation).where(
            and_(Reservation.book_id == book_id,Reservation.status == ReservationStatus.IN_QUEUE
            )
        )
        queue_result = await db.execute(queue_query)
        scheduled_reservers = queue_result.scalars().all()

        return {
            "current_holders": current_holders,
            "scheduled_reservers": scheduled_reservers
        }