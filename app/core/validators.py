from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal

class EntityValidator(BaseModel):
    class Config:
        validate_assignment = True
        # orm_mode = True
        from_attributes = True
        arbitrary_types_allowed = True

    @field_validator('*')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v