from fastapi import Request, HTTPException, status
from typing import Optional
from app.schemas.error import ErrorResponse

async def validation_error_handler(request: Request, exc: Exception) -> ErrorResponse:
    if isinstance(exc, HTTPException):
        return ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(exc.detail),
                details={"status_code": exc.status_code}
            )
        )
    return ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_ERROR",
            message="An internal error occurred"
        )
    )