"""公开接口 - 无需登录"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime
from typing import List
from TourOps.core.database import get_db
from TourOps.models.trip import Trip
from TourOps.models.activity import Activity, ActivityType

router = APIRouter()

class ActivityDetail(BaseModel):
    id: int
    type: ActivityType
    name: str
    start_time: datetime
    end_time: datetime
    location: str | None
    notes: str | None
    
    class Config:
        from_attributes = True

class TripDetail(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    guest_count: int
    activities: List[ActivityDetail] = []
    
    class Config:
        from_attributes = True

@router.get("/trips/{share_code}", response_model=TripDetail)
def get_shared_trip(share_code: str, db: Session = Depends(get_db)):
    """通过分享码查看行程详情（公开接口，无需登录）"""
    trip = db.query(Trip).filter(Trip.share_code == share_code).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在或链接已失效")
    
    activities = db.query(Activity).filter(Activity.trip_id == trip.id).order_by(Activity.sort_order, Activity.start_time).all()
    
    return TripDetail(
        id=trip.id,
        name=trip.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        guest_count=trip.guest_count,
        activities=[ActivityDetail.model_validate(a) for a in activities]
    )
