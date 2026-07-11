"""活动服务"""
from sqlalchemy.orm import Session
from typing import List, Optional
from TourOps.models.activity import Activity
from TourOps.schemas.activity import ActivityCreate, ActivityUpdate

class ActivityService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_list_by_trip(self, trip_id: int) -> List[Activity]:
        return self.db.query(Activity).filter(
            Activity.trip_id == trip_id
        ).order_by(Activity.sort_order, Activity.start_time).all()
    
    def get_by_id(self, activity_id: int, trip_id: int = None) -> Optional[Activity]:
        query = self.db.query(Activity).filter(Activity.id == activity_id)
        if trip_id:
            query = query.filter(Activity.trip_id == trip_id)
        return query.first()
    
    def create(self, activity_in: ActivityCreate, trip_id: int) -> Activity:
        activity = Activity(**activity_in.model_dump(), trip_id=trip_id)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def update(self, activity: Activity, activity_in: ActivityUpdate) -> Activity:
        for field, value in activity_in.model_dump(exclude_unset=True).items():
            setattr(activity, field, value)
        self.db.commit()
        self.db.refresh(activity)
        return activity
    
    def delete(self, activity: Activity) -> None:
        self.db.delete(activity)
        self.db.commit()
