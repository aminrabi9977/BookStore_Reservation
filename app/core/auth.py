from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.customer import Customer
from app.core.security import SecurityService, SecurityConfig 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
    ) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = SecurityService.verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        if await SecurityService.is_token_blacklisted(user_id):
            raise credentials_exception    
    except JWTError:
        raise credentials_exception

    user = await get_user(db, int(user_id))
    
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

async def get_current_customer(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Customer:
    if current_user.role != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a customer"
        )
    
    query = select(Customer).where(Customer.user_id == current_user.id)
    result = await db.execute(query)
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    return customer


def check_user_role(required_roles: list):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
    return role_checker