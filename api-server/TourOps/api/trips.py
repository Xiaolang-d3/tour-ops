from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from datetime import date
import secrets
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user, require_admin
from TourOps.models.user import User
from TourOps.models.trip import Trip, TripStatus
from TourOps.models.activity import Activity
from TourOps.schemas.trip import TripCreate, TripUpdate, TripResponse
from TourOps.services.trip_service import TripService

router = APIRouter()


def _get_user_trip_or_404(trip_id: int, user: User, db: Session) -> Trip:
    """获取当前用户的行程，不存在或不属于当前用户则 404"""
    service = TripService(db)
    trip = service.get_user_trip(trip_id, user.id)
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


def _check_date_conflict(db: Session, user_id: int, start_date: date, end_date: date, exclude_trip_id: int | None = None):
    """检测日期冲突，有冲突则抛出 HTTP 409"""
    query = db.query(Trip).filter(
        Trip.created_by == user_id,
        Trip.status.notin_([TripStatus.CANCELLED]),
        Trip.start_date <= end_date,
        Trip.end_date >= start_date,
    )
    if exclude_trip_id:
        query = query.filter(Trip.id != exclude_trip_id)

    conflicts = query.all()
    if conflicts:
        names = "、".join(f"「{t.name}」({t.start_date} ~ {t.end_date})" for t in conflicts)
        raise HTTPException(
            status_code=409,
            detail=f"该时间段与已有行程存在冲突：{names}，同一时间段只能有一个行程。"
        )


@router.get("/check-date-conflict")
def check_date_conflict(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    exclude_trip_id: int | None = Query(None, description="排除的行程ID（编辑时使用）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """检测日期范围与用户现有行程是否冲突"""
    query = db.query(Trip).filter(
        Trip.created_by == current_user.id,
        Trip.status.notin_([TripStatus.CANCELLED]),
        # 日期区间重叠判断：A.start <= B.end AND A.end >= B.start
        Trip.start_date <= end_date,
        Trip.end_date >= start_date,
    )
    if exclude_trip_id:
        query = query.filter(Trip.id != exclude_trip_id)

    conflicts = query.all()
    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": [
            {
                "id": t.id,
                "name": t.name,
                "start_date": t.start_date.isoformat(),
                "end_date": t.end_date.isoformat(),
                "status": t.status.value,
            }
            for t in conflicts
        ],
    }


@router.get("", response_model=List[TripResponse])
def list_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取当前用户行程列表"""
    service = TripService(db)
    return service.get_list(current_user.id)


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip_in: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建行程"""
    _check_date_conflict(db, current_user.id, trip_in.start_date, trip_in.end_date)
    service = TripService(db)
    return service.create(trip_in, current_user.id)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取行程详情（仅限自己的行程）"""
    return _get_user_trip_or_404(trip_id, current_user, db)


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: int, trip_in: TripUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新行程（仅限自己的行程）"""
    trip = _get_user_trip_or_404(trip_id, current_user, db)
    service = TripService(db)
    return service.update(trip, trip_in)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除行程（仅限自己的行程）"""
    trip = _get_user_trip_or_404(trip_id, current_user, db)
    service = TripService(db)
    service.delete(trip)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{trip_id}/copy", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def copy_trip(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """复制行程（仅限自己的行程）"""
    original = _get_user_trip_or_404(trip_id, current_user, db)
    
    # 检测日期冲突（排除原行程自身）
    _check_date_conflict(db, current_user.id, original.start_date, original.end_date, exclude_trip_id=original.id)
    
    # 复制行程
    new_trip = Trip(
        name=f"{original.name} (副本)",
        start_date=original.start_date,
        end_date=original.end_date,
        guest_count=original.guest_count,
        budget=original.budget,
        preferences=original.preferences,
        special_requirements=original.special_requirements,
        status=original.status,
        share_code=secrets.token_hex(16),
        created_by=current_user.id
    )
    db.add(new_trip)
    db.flush()
    
    # 复制活动
    activities = db.query(Activity).filter(Activity.trip_id == trip_id).all()
    for act in activities:
        new_activity = Activity(
            trip_id=new_trip.id,
            type=act.type,
            name=act.name,
            start_time=act.start_time,
            end_time=act.end_time,
            location=act.location,
            cost=act.cost,
            notes=act.notes,
            sort_order=act.sort_order,
            guide_id=act.guide_id,
            vehicle_id=act.vehicle_id,
            hotel_id=act.hotel_id,
            restaurant_id=act.restaurant_id
        )
        db.add(new_activity)
    
    db.commit()
    db.refresh(new_trip)
    return new_trip


# ==================== 管理员接口 ====================

@router.get("/admin/all")
def admin_list_all_trips(
    status: str | None = Query(None, description="按状态筛选"),
    keyword: str | None = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理员查看所有行程"""
    query = db.query(Trip)
    if status:
        query = query.filter(Trip.status == status)
    if keyword:
        query = query.filter(Trip.name.contains(keyword))
    trips = query.order_by(Trip.created_at.desc()).all()

    # 附带创建者信息
    user_ids = list({t.created_by for t in trips})
    users_map = {}
    if user_ids:
        from TourOps.models.user import User as UserModel
        users = db.query(UserModel).filter(UserModel.id.in_(user_ids)).all()
        users_map = {u.id: {"id": u.id, "username": u.username, "name": u.name, "avatar": u.avatar} for u in users}

    result = []
    for t in trips:
        activity_count = db.query(Activity).filter(Activity.trip_id == t.id).count()
        result.append({
            "id": t.id,
            "name": t.name,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "end_date": t.end_date.isoformat() if t.end_date else None,
            "guest_count": t.guest_count,
            "budget": float(t.budget) if t.budget else None,
            "status": t.status.value,
            "share_code": t.share_code,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "activity_count": activity_count,
            "creator": users_map.get(t.created_by),
        })
    return result


@router.put("/admin/{trip_id}/status")
def admin_update_trip_status(
    trip_id: int,
    status_in: TripUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理员修改行程状态"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    if status_in.status:
        trip.status = status_in.status
    db.commit()
    db.refresh(trip)
    return {"id": trip.id, "status": trip.status.value}


@router.delete("/admin/{trip_id}")
def admin_delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """管理员删除行程"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    # 先删活动再删行程
    db.query(Activity).filter(Activity.trip_id == trip_id).delete(synchronize_session=False)
    db.delete(trip)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
