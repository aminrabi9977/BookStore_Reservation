from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets
import string

class SecurityConfig:
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityService:
    _token_blacklist = set() 

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters long")
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            SecurityConfig.SECRET_KEY, 
            algorithm=SecurityConfig.ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(
                token, 
                SecurityConfig.SECRET_KEY, 
                algorithms=[SecurityConfig.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode, 
            SecurityConfig.SECRET_KEY, 
            algorithm=SecurityConfig.ALGORITHM
        )

    @staticmethod
    def generate_password_reset_token() -> str:
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    @classmethod
    async def blacklist_user_token(cls, user_id: int) -> None:
        cls._token_blacklist.add(str(user_id))

    @classmethod
    async def remove_from_blacklist(cls, user_id: int) -> None:
        cls._token_blacklist.discard(str(user_id))

    @classmethod
    async def is_token_blacklisted(cls, user_id: str) -> bool:
        return user_id in cls._token_blacklist

    @staticmethod
    def get_token_expiration(token: str) -> datetime:
        try:
            payload = jwt.decode(token, SecurityConfig.SECRET_KEY, algorithms=[SecurityConfig.ALGORITHM]
            )
            exp = payload.get("exp")
            if exp is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has no expiration"
                )
            return datetime.fromtimestamp(exp)
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    @staticmethod
    async def validate_token_not_expired(token: str) -> bool:
        exp_date = SecurityService.get_token_expiration(token)
        return datetime.utcnow() < exp_date