"""行程服务"""
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
from TourOps.models.trip import Trip
from TourOps.schemas.trip import TripCreate, TripUpdate

class TripService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_list(self, user_id: int) -> List[Trip]:
        return self.db.query(Trip).filter(Trip.created_by == user_id).all()
    
    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        return self.db.query(Trip).filter(Trip.id == trip_id).first()
    
    def get_user_trip(self, trip_id: int, user_id: int) -> Optional[Trip]:
        """获取指定用户的行程（带归属校验）"""
        return self.db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.created_by == user_id
        ).first()
    
    def get_by_share_code(self, share_code: str) -> Optional[Trip]:
        return self.db.query(Trip).filter(Trip.share_code == share_code).first()
    
    def create(self, trip_in: TripCreate, user_id: int) -> Trip:
        trip = Trip(
            **trip_in.model_dump(),
            created_by=user_id,
            share_code=secrets.token_hex(16)
        )
        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def update(self, trip: Trip, trip_in: TripUpdate) -> Trip:
        for field, value in trip_in.model_dump(exclude_unset=True).items():
            setattr(trip, field, value)
        self.db.commit()
        self.db.refresh(trip)
        return trip
    
    def delete(self, trip: Trip) -> None:
        self.db.delete(trip)
        self.db.commit()
