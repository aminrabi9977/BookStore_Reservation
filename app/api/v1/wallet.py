from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.auth import get_current_customer
from app.schemas.wallet import WalletTransaction, WalletStatus
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("/charge", response_model=WalletStatus)
async def charge_wallet(
    transaction: WalletTransaction,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    return await WalletService.charge_wallet(current_customer, transaction, db)

@router.get("/status", response_model=WalletStatus)
async def get_wallet_status(
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_db)
):
    return await WalletService.get_wallet_status(current_customer, db)