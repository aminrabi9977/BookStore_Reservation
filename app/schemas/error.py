from pydantic import BaseModel
from typing import Optional, Any

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict[str, Any]] = None

class ValidationError(BaseModel):
    field: str
    message: str

class ErrorResponse(BaseModel):
    status: str = "error"
    error: ErrorDetail
    validation_errors: Optional[list[ValidationError]] = None