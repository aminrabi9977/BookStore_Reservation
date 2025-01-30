
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.services.reservation_service import ReservationService
from app.services.purchasing_service import PurchasingService
from app.models.reservation import Reservation, ReservationStatus
from app.models.book import Book
from app.models.customer import Customer, SubscriptionModel
from app.schemas.reservation import ReservationCreate, ReservationResponse, ReservationActionResponse,ReservationError, UserLimitsResponse , QueueStatusResponse
from app.core.auth import get_current_customer
# from app.core.queue import ReservationQueue
from app.core.auth import get_current_customer
from app.services.book_service import BookService
from app.services.reservation_service import ReservationService
from app.services.queue_manager import QueueManager
router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationActionResponse)
async def create_reservation(
    reservation: ReservationCreate,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    
    if current_customer.subscription_type == SubscriptionType.FREE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="Free users cannot reserve books"
        )
    if not await ReservationService.validate_reservation_limits(current_customer, db):
        return ReservationActionResponse(status="error",
            error={
                "error_type": "limit_exceeded",
                "detail": "Maximum reservation limit reached"
            }
        )
    book = await BookService.get_book(db, reservation.book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    days = (reservation.end_time - reservation.start_time).days
    is_valid, cost = await ReservationService.validate_wallet_amount(current_customer, 
        days,db
    )

    if not is_valid:
        missing_amount = cost - current_customer.wallet_amount
        return ReservationActionResponse(status="error",
            error={
                "error_type": "insufficient_funds",
                "detail": "Insufficient wallet balance",
                "required_amount": cost
            },
            wallet_redirect={
                "required_amount": cost,
                "current_balance": current_customer.wallet_balance,
                "missing_amount": missing_amount
            }
        )

    if book.available_units > 0:
        reservation = await ReservationService.create_instant_reservation(
            customer=current_customer,
            book_id=book.id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            price=cost,
            db=db
        )
        return ReservationActionResponse(status="reserved",
            reservation_id=reservation.id
        )
    else:
        queue_position = await QueueManager().add_to_queue(
            reservation=reservation,
            customer=current_customer,
            db=db
        )
        return ReservationActionResponse(
            status="queued",
            queue_position=queue_position
        )

@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    reservation = await ReservationService.get_reservation(
        reservation_id=reservation_id,
        customer_id=current_customer.id,
        db=db
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    return reservation

@router.get("/queue-status", response_model=List[QueueStatusResponse])
async def get_queue_status(
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    queued_reservations = await ReservationService.get_customer_queue_status(
        customer_id=current_customer.id,db=db
    )
    return queued_reservations

@router.post("/queue-exit/{reservation_id}")
async def exit_queue(
    reservation_id: int,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    success = await ReservationService.exit_queue(
        reservation_id=reservation_id,
        customer_id=current_customer.id,
        db=db
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found in queue"
        )
    return {"message": "Successfully exited queue"}

@router.get("/user-limits", response_model=UserLimitsResponse)
async def get_user_limits(current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    active_count = await ReservationService.get_active_reservations_count(
        customer_id=current_customer.id,
        db=db
    )
    max_allowed = 10 if current_customer.subscription_model == SubscriptionModal.PREMIUM else 5
    return UserLimitsResponse(
        active_reservations=active_count,
        max_allowed=max_allowed,
        remaining=max_allowed - active_count
    )  s