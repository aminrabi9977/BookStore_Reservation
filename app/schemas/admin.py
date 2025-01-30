from pydantic import BaseModel
from typing import List
from datetime import datetime

class ReservationDetail(BaseModel):
    id: int
    customer_id: int
    start_time: datetime
    end_time: datetime
    status: str

    class Config:
        # orm_mode = True
        from_attributes = True

class BookReservationsResponse(BaseModel):
    current_holders: List[ReservationDetail]
    scheduled_reservers: List[ReservationDetail]

    class Config:
        # orm_mode = True
        from_attributes = True  
class AdminActionResponse(BaseModel):
    message: str