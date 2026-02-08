from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user
from TourOps.models.user import User
from TourOps.models.trip import Trip
from TourOps.models.activity import Activity
from TourOps.schemas.activity import ActivityCreate, ActivityUpdate, ActivityResponse
from TourOps.services.activity_service import ActivityService
from TourOps.services.conflict_service import ConflictService


class ReorderItem(BaseModel):
    id: int
    sort_order: int


class ReorderRequest(BaseModel):
    items: List[ReorderItem]


class ConflictCheckRequest(BaseModel):
    start_time: str
    end_time: str
    exclude_activity_id: int | None = None

router = APIRouter()


def _verify_trip_ownership(trip_id: int, user: User, db: Session) -> Trip:
    """校验行程归属于当前用户，返回行程对象"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


@router.get("/{trip_id}/activities", response_model=List[ActivityResponse])
def list_activities(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取行程下的活动列表"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ActivityService(db)
    return service.get_list_by_trip(trip_id)


@router.post("/{trip_id}/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(trip_id: int, activity_in: ActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建活动"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ActivityService(db)
    return service.create(activity_in, trip_id)


@router.get("/{trip_id}/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(trip_id: int, activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取活动详情"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ActivityService(db)
    activity = service.get_by_id(activity_id, trip_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return activity


@router.put("/{trip_id}/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(trip_id: int, activity_id: int, activity_in: ActivityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新活动"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ActivityService(db)
    activity = service.get_by_id(activity_id, trip_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return service.update(activity, activity_in)


@router.delete("/{trip_id}/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(trip_id: int, activity_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除活动"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ActivityService(db)
    activity = service.get_by_id(activity_id, trip_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    service.delete(activity)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{trip_id}/activities/reorder")
def reorder_activities(trip_id: int, request: ReorderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """批量更新活动排序"""
    _verify_trip_ownership(trip_id, current_user, db)
    for item in request.items:
        activity = db.query(Activity).filter(Activity.id == item.id, Activity.trip_id == trip_id).first()
        if activity:
            activity.sort_order = item.sort_order
    db.commit()
    return {"message": "排序更新成功", "count": len(request.items)}


@router.post("/{trip_id}/activities/check-conflict")
def check_time_conflict(trip_id: int, request: ConflictCheckRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """检测活动时间冲突"""
    _verify_trip_ownership(trip_id, current_user, db)
    from datetime import datetime
    service = ConflictService(db)
    start_time = datetime.fromisoformat(request.start_time)
    end_time = datetime.fromisoformat(request.end_time)
    conflicts = service.check_time_conflict(trip_id, start_time, end_time, request.exclude_activity_id)
    return {"has_conflict": len(conflicts) > 0, "conflicts": conflicts}
