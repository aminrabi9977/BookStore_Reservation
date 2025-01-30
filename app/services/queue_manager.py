from typing import Dict, List, Optional
from datetime import datetime
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.reservation import Reservation, ReservationStatus
from app.models.customer import Customer, SubscriptionModel
from app.models.book import Book

class QueueManager:
    _instance = None
    _queues: Dict[int, List[dict]] = {}  
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueueManager, cls).__new__(cls)
        return cls._instance

    async def get_queue(self, book_id: int) -> List[Reservation]:
        #gereftan hame reservation dar queue baraye book
        return self._queues.get(book_id, [])

    async def add_to_queue(self,reservation: Reservation,
        customer: Customer,
        db: AsyncSession) -> int:
        async with self._lock:
            book_id = reservation.book_id
            if book_id not in self._queues:
                self._queues[book_id] = []

            queue_entry = {
                "reservation_id": reservation.id,"customer_id": customer.id,"subscription_model": customer.subscription_model,"requested_at": datetime.now()
            }

            queue = self._queues[book_id]
            position = 0

            if customer.subscription_model == SubscriptionModel.PREMIUM:
                while (position < len(queue) and 
                       queue[position]["subscription_model"] == SubscriptionModel.PREMIUM):
                    position += 1
            else:
                # ezefe kardan be akhar queue
                position = len(queue)

            self._queues[book_id].insert(position, queue_entry)
            
            reservation.status = ReservationStatus.IN_QUEUE
            await db.commit()
            
            return position + 1  

    async def remove_from_queue(self,book_id: int,reservation_id: int) -> None:
        """Remove a reservation from queue"""
        async with self._lock:
            if book_id in self._queues:
                self._queues[book_id] = [
                    entry for entry in self._queues[book_id]
                    if entry["reservation_id"] != reservation_id
                ]

    async def get_queue_position(self,
        book_id: int,
        reservation_id: int) -> Optional[int]:
        if book_id not in self._queues:
            return None
        for i, entry in enumerate(self._queues[book_id]):
            if entry["reservation_id"] == reservation_id:
                return i + 1
        return None

    async def get_next_in_queue(self,
        book_id: int) -> Optional[dict]:
        async with self._lock:
            if book_id in self._queues and self._queues[book_id]:
                return self._queues[book_id][0]
            return None

    async def reorder_queue(self,
        book_id: int,
        db: AsyncSession) -> None:
        async with self._lock:
            if book_id not in self._queues:
                return

            self._queues[book_id].sort(
                key=lambda x: (
                    x["subscription_model"] != SubscriptionModel.PREMIUM,
                    x["requested_at"]
                )
            )

    async def get_estimated_wait_time(self,
        book_id: int,
        position: int,
        db: AsyncSession) -> Optional[int]:
        if position <= 0:
            return None
        query = select(Reservation).where(
            and_(Reservation.book_id == book_id,Reservation.status == ReservationStatus.COMPLETED
            )).limit(10) 
        
        result = await db.execute(query)
        completed_reservations = result.scalars().all()
        
        if not completed_reservations:
            return None
            
        total_duration = sum(
            (r.end_time - r.start_time).total_seconds() 
            for r in completed_reservations
        )
        avg_duration = total_duration / len(completed_reservations)
        
        return int((avg_duration * position) / 60)  