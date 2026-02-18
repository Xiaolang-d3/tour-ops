from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from TourOps.models.trip import TripStatus

class TripCreate(BaseModel):
    name: str
    trip_type: str | None = None
    start_date: date
    end_date: date
    guest_count: int = 1
    budget: Decimal | None = None
    preferences: Any | None = None
    special_requirements: Any | None = None

class TripUpdate(BaseModel):
    name: str | None = None
    trip_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    guest_count: int | None = None
    budget: Decimal | None = None
    preferences: Any | None = None
    special_requirements: Any | None = None
    status: TripStatus | None = None

class TripResponse(BaseModel):
    id: int
    name: str
    trip_type: str | None = None
    start_date: date
    end_date: date
    guest_count: int
    budget: Decimal | None
    preferences: Any | None
    status: TripStatus
    share_code: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True
