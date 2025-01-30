from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class QueueStatus(str, Enum):
    WAITING = "waiting"
    PROCESSING = "processing"
    FAILED = "failed"
    CANCELLED = "cancelled"

class QueueEntry(BaseModel):
    id: int
    book_id: int
    customer_id: int
    start_time: datetime
    end_time: datetime
    position: int
    requested_at: datetime
    status: QueueStatus
    estimated_wait_time: Optional[int] = None  

class QueueExitResponse(BaseModel):
    success: bool
    message: str