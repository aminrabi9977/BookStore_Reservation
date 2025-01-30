
from fastapi import Request, status, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import BookStoreException
import logging

logger = logging.getLogger(__name__)

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, BookStoreException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error_code": exc.error_code,
                "detail": exc.detail,
                "extra": exc.extra}
        )

   
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error_code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred"}
    )