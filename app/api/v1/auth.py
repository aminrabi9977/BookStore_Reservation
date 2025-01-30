from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import timedelta

from app.database import get_db
from app.models.user import User
from app.core.security import SecurityService, SecurityConfig
from app.services.otp_services import OTPService
from app.schemas.auth import UserLogin, OTPVerification
from app.schemas.auth_token import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

# @router.post("/login", response_model=Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_db)
# ):
#     query = select(User).where(User.username == form_data.username)
#     result = await db.execute(query)
#     user = result.scalar_one_or_none()
    
#     if not user or not SecurityService.verify_password(form_data.password, user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
    
#     access_token_expires = timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES) 
#     access_token = SecurityService.create_access_token( 
#         data={"sub": str(user.id)},
#         expires_delta=access_token_expires
#     )
    
#     return {"access_token": access_token, "token_type": "bearer"}



@router.post("/signup", response_model=UserResponse)
async def signup(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    
    query = select(User).where(
        or_(User.email == user.email, User.username == user.username)
    )
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    
    hashed_password = SecurityService.get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user    




@router.post("/login/request-otp")
async def request_otp(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.username == user_credentials.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user or not SecurityService.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    
    otp = OTPService.generate_otp(user.phone)
    return {"message": "OTP sent successfully (check console)"}

@router.post("/login/verify-otp", response_model = Token)
async def verify_otp(
    otp_verification: OTPVerification,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.username == otp_verification.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not OTPService.verify_otp(user.phone, otp_verification.otp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    access_token = SecurityService.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}    