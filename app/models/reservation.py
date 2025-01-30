from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import List
from decimal import Decimal
from enum import Enum

from app.database import Base
from app.core.exceptions import ValidationError

class ReservationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_QUEUE = "in_queue"
    QUEUE_CANCELLED = "queue_cancelled"
    ENDED_EARLY = "ended_early"
    FAILED = "failed"

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    status = Column(SQLAlchemyEnum(ReservationStatus), nullable=False, default=ReservationStatus.PENDING)

    # Relationships
    customer = relationship("Customer", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")

    def __init__(self, **kwargs):
        self.validate_dates(kwargs.get('start_time'), kwargs.get('end_time'))
        self.validate_price(kwargs.get('price', 0))
        super().__init__(**kwargs)

    @staticmethod
    def validate_dates(start_time: datetime, end_time: datetime):
        if not start_time or not end_time:
            raise ValidationError("Start and end times are required")
        if start_time >= end_time:
            raise ValidationError("End time must be after start time")

    @staticmethod
    def validate_price(price: float):
        if price < 0:
            raise ValidationError("Price must be non-negative")

    @staticmethod
    def validate_reservation_period(
        start_time: datetime,
        end_time: datetime,
        subscription_type: str
    ) -> List[str]:
        errors = []
        max_days = 14 if subscription_type == "PREMIUM" else 7
        
        if start_time < datetime.now():
            errors.append("Start time must be in the future")
            
        if (end_time - start_time).days > max_days:
            errors.append(f"Maximum reservation period is {max_days} days")
            
        return errors

    def update_status(self, new_status: ReservationStatus):
        if new_status not in ReservationStatus:
            raise ValidationError("Invalid reservation status")
        self.status = new_status

    def extend_reservation(self, days: int, subscription_type: str):
        new_end_time = self.end_time + timedelta(days=days)
        errors = self.validate_reservation_period(self.start_time, new_end_time, subscription_type)
        if errors:
            raise ValidationError(errors[0])
        self.end_time = new_end_time

    def cancel_reservation(self):
        if self.status not in [ReservationStatus.PENDING, ReservationStatus.IN_QUEUE]:
            raise ValidationError("Cannot cancel reservation in current status")
        self.status = ReservationStatus.CANCELLED

    def is_active(self) -> bool:
        return self.status == ReservationStatus.ACTIVE

    def is_in_queue(self) -> bool:
        return self.status == ReservationStatus.IN_QUEUE