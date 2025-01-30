from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.core.auth import get_current_admin_user, get_current_user
from app.services.admin_service import AdminService
from app.schemas.admin import (BookReservationsResponse,AdminActionResponse)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/users/{user_id}/revoke-token", response_model=AdminActionResponse)
async def revoke_user_token(user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    success = await AdminService.revoke_user_token(current_admin, user_id, db)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke admin token"
        )
    return {"message": "Token revoked successfully"}

@router.post("/reservations/{reservation_id}/end", response_model=AdminActionResponse)
async def end_reservation(
    reservation_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    success = await AdminService.end_reservation_early(reservation_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found or already ended"
        )
    return {"message": "Reservation ended successfully"}

@router.get("/books/{book_id}/reservations", response_model=BookReservationsResponse)
async def get_book_reservations(
    book_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    return await AdminService.get_book_reservations(book_id, db)