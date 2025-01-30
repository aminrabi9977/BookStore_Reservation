from fastapi import HTTPException, status, Request
from typing import Optional, Any, Dict
from app.schemas.error import ErrorResponse, ErrorDetail

class BookStoreException(HTTPException):
    def __init__(self,status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class InsufficientFundsError(BookStoreException):
    def __init__(self, required_amount: float):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Required: {required_amount} Toman"
        )

class BookNotAvailableError(BookStoreException):
    def __init__(self, book_id: int):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book {book_id} is not available for reservation"
        )

class ReservationLimitExceededError(BookStoreException):
    def __init__(self, subscription_model: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum reservation limit reached for {subscription_model} subscription"
        )


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500,content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message=str(exc)
            )
        ).dict()
    )



class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = extra or {}

class EntityNotFoundError(AppException):
    def __init__(self, entity: str, entity_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} with id {entity_id} not found",
            error_code="ENTITY_NOT_FOUND"
        )

class ValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

class AuthorizationError(AppException):
    def __init__(self, detail: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )

class BusinessError(AppException):
    def __init__(self, detail: str, error_code: str = "BUSINESS_RULE_ERROR"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code=error_code
        )