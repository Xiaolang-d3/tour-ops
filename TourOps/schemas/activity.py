from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from TourOps.models.activity import ActivityType

class ActivityCreate(BaseModel):
    type: ActivityType
    name: str
    start_time: datetime
    end_time: datetime
    location: str | None = None
    cost: Decimal | None = None
    notes: str | None = None
    sort_order: int = 0
    guide_id: int | None = None
    vehicle_id: int | None = None
    hotel_id: int | None = None
    restaurant_id: int | None = None

class ActivityUpdate(BaseModel):
    type: ActivityType | None = None
    name: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    cost: Decimal | None = None
    notes: str | None = None
    sort_order: int | None = None
    guide_id: int | None = None
    vehicle_id: int | None = None
    hotel_id: int | None = None
    restaurant_id: int | None = None

class ActivityResponse(BaseModel):
    id: int
    trip_id: int
    type: ActivityType
    name: str
    start_time: datetime
    end_time: datetime
    location: str | None
    cost: Decimal | None
    notes: str | None
    sort_order: int
    guide_id: int | None = None
    vehicle_id: int | None = None
    hotel_id: int | None = None
    restaurant_id: int | None = None
    
    class Config:
        from_attributes = True
