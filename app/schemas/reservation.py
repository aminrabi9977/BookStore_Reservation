from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
from decimal import Decimal
class ReservationStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_QUEUE = "in_queue"
    QUEUE_CANCELLED = "queue_cancelled"
    ENDED_EARLY = "ended_early"
    FAILED = "failed"

class ReservationBase(BaseModel):
    book_id: int
    start_time: datetime
    end_time: datetime

    @field_validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

    @field_validator('start_time')
    def start_time_must_be_future(cls, v):
        if v < datetime.now():
            raise ValueError('start_time must be in the future')
        return v

class ReservationCreate(ReservationBase):
    pass

class ReservationError(BaseModel):
    error_type: str
    detail: str
    required_amount: Optional[float] = None

class WalletRedirect(BaseModel):
    redirect_type: str = "wallet_charge"
    required_amount: float
    current_balance: float
    missing_amount: float


class ReservationUpdate(BaseModel):
    status: Optional[ReservationStatus]
    end_time: Optional[datetime]

    @field_validator('end_time')
    def end_time_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('end_time must be in the future')
        return v

class ReservationResponse(ReservationBase):
    id: int
    customer_id: int
    price: float
    status: ReservationStatus
    
    
    class BookInfo(BaseModel):
        id: int
        title: str
        isbn: str

    class CustomerInfo(BaseModel):
        id: int
        username: str
        subscription_type: str

    book: BookInfo
    customer: CustomerInfo

    class Config:
        from_attributes = True

class ReservationInQueue(BaseModel):
    id: int
    book_id: int
    customer_id: int
    requested_start_time: datetime
    requested_end_time: datetime
    queue_position: int
    
    class Config:
        from_attributes = True

class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus

class ExtendReservation(BaseModel):
    additional_days: int

    @field_validator('additional_days')
    def validate_additional_days(cls, v):
        if v <= 0:
            raise ValueError('additional_days must be positive')
        if v > 14:  
            raise ValueError('cannot extend more than 14 days')
        return v

class ReservationStats(BaseModel):
    total_active: int
    total_completed: int
    total_in_queue: int
    total_cancelled: int
    average_duration_days: float
    total_spent: float

    class Config:
        from_attributes = True

class ReservationFilter(BaseModel):
    status: Optional[ReservationStatus]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    book_id: Optional[int]
    customer_id: Optional[int]

class QueuePosition(BaseModel):
    position: int
    estimated_wait_days: Optional[float]

    class Config:
        from_attributes = True

class ReservationActionResponse(BaseModel):
    status: str
    reservation_id: Optional[int] = None
    queue_position: Optional[int] = None
    error: Optional[ReservationError] = None
    wallet_redirect: Optional[WalletRedirect] = None

class QueueStatusResponse(BaseModel):
    book_id: int
    position: int
    requested_at: datetime
    estimated_wait_time: Optional[int] = None

class UserLimitsResponse(BaseModel):
    active_reservations: int
    max_allowed: int
    remaining: int


class ReservationValidationResponse(BaseModel):
    is_valid: bool
    errors: Optional[list[str]] = None
    required_wallet_amount: Optional[Decimal] = None
    current_wallet_balance: Optional[Decimal] = None
    missing_amount: Optional[Decimal] = None
    queue_position: Optional[int] = None
    estimated_wait_time: Optional[int] = None

class ReservationLimitResponse(BaseModel):
    current_count: int
    max_allowed: int
    remaining: int
    subscription_type: str