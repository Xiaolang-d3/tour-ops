"""冲突检测服务"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from TourOps.models.activity import Activity
from TourOps.models.trip import Trip


class ConflictService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_time_conflict(
        self,
        trip_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_activity_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        检测同一行程内活动时间冲突
        返回冲突的活动列表
        """
        query = self.db.query(Activity).filter(
            Activity.trip_id == trip_id,
            or_(
                # 新活动开始时间在已有活动时间范围内
                and_(Activity.start_time <= start_time, Activity.end_time > start_time),
                # 新活动结束时间在已有活动时间范围内
                and_(Activity.start_time < end_time, Activity.end_time >= end_time),
                # 新活动完全包含已有活动
                and_(Activity.start_time >= start_time, Activity.end_time <= end_time)
            )
        )
        
        if exclude_activity_id:
            query = query.filter(Activity.id != exclude_activity_id)
        
        conflicts = query.all()
        return [
            {
                "id": act.id,
                "name": act.name,
                "start_time": act.start_time.isoformat(),
                "end_time": act.end_time.isoformat(),
                "type": act.type.value
            }
            for act in conflicts
        ]
    
    def check_resource_conflict(
        self,
        resource_type: str,
        resource_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_activity_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        检测资源冲突（同一资源在同一时段被多次分配）
        resource_type: guide, vehicle, hotel, restaurant
        """
        resource_field_map = {
            "guide": Activity.guide_id,
            "vehicle": Activity.vehicle_id,
            "hotel": Activity.hotel_id,
            "restaurant": Activity.restaurant_id,
        }
        
        if resource_type not in resource_field_map:
            return []
        
        resource_field = resource_field_map[resource_type]
        
        query = self.db.query(Activity).filter(
            resource_field == resource_id,
            or_(
                and_(Activity.start_time <= start_time, Activity.end_time > start_time),
                and_(Activity.start_time < end_time, Activity.end_time >= end_time),
                and_(Activity.start_time >= start_time, Activity.end_time <= end_time)
            )
        )
        
        if exclude_activity_id:
            query = query.filter(Activity.id != exclude_activity_id)
        
        conflicts = query.all()
        
        result = []
        for act in conflicts:
            trip = self.db.query(Trip).filter(Trip.id == act.trip_id).first()
            result.append({
                "activity_id": act.id,
                "activity_name": act.name,
                "trip_id": act.trip_id,
                "trip_name": trip.name if trip else "未知行程",
                "start_time": act.start_time.isoformat(),
                "end_time": act.end_time.isoformat(),
            })
        
        return result
    
    def get_resource_schedule(
        self,
        resource_type: str,
        resource_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取资源在指定时间段内的占用情况
        """
        resource_field_map = {
            "guide": Activity.guide_id,
            "vehicle": Activity.vehicle_id,
            "hotel": Activity.hotel_id,
            "restaurant": Activity.restaurant_id,
        }
        
        if resource_type not in resource_field_map:
            return []
        
        resource_field = resource_field_map[resource_type]
        
        activities = self.db.query(Activity).filter(
            resource_field == resource_id,
            Activity.start_time >= start_date,
            Activity.end_time <= end_date
        ).order_by(Activity.start_time).all()
        
        result = []
        for act in activities:
            trip = self.db.query(Trip).filter(Trip.id == act.trip_id).first()
            result.append({
                "activity_id": act.id,
                "activity_name": act.name,
                "trip_id": act.trip_id,
                "trip_name": trip.name if trip else "未知行程",
                "start_time": act.start_time.isoformat(),
                "end_time": act.end_time.isoformat(),
            })
        
        return result
