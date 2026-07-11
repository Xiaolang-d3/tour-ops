from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user, require_admin
from TourOps.models.user import User
from TourOps.models.resource import Guide, Vehicle, Hotel, Restaurant
from TourOps.services.resource_service import ResourceService
from TourOps.services.conflict_service import ConflictService

router = APIRouter()

# 导游
@router.get("/guides")
def list_guides(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取导游列表"""
    service = ResourceService(db)
    return service.get_guides()

@router.post("/guides", status_code=status.HTTP_201_CREATED)
def create_guide(data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建导游（管理员）"""
    service = ResourceService(db)
    return service.create(Guide, data)

# 车辆
@router.get("/vehicles")
def list_vehicles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取车辆列表"""
    service = ResourceService(db)
    return service.get_vehicles()

@router.post("/vehicles", status_code=status.HTTP_201_CREATED)
def create_vehicle(data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建车辆（管理员）"""
    service = ResourceService(db)
    return service.create(Vehicle, data)

# 酒店
@router.get("/hotels")
def list_hotels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取酒店列表"""
    service = ResourceService(db)
    return service.get_hotels()

@router.post("/hotels", status_code=status.HTTP_201_CREATED)
def create_hotel(data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建酒店（管理员）"""
    service = ResourceService(db)
    return service.create(Hotel, data)

# 餐厅
@router.get("/restaurants")
def list_restaurants(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取餐厅列表"""
    service = ResourceService(db)
    return service.get_restaurants()

@router.post("/restaurants", status_code=status.HTTP_201_CREATED)
def create_restaurant(data: dict, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建餐厅（管理员）"""
    service = ResourceService(db)
    return service.create(Restaurant, data)


# 删除资源（管理员）
@router.delete("/guides/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_guide(resource_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """删除导游（管理员）"""
    service = ResourceService(db)
    resource = service.get_by_id(Guide, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    service.delete(resource)

@router.delete("/vehicles/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(resource_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """删除车辆（管理员）"""
    service = ResourceService(db)
    resource = service.get_by_id(Vehicle, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    service.delete(resource)

@router.delete("/hotels/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hotel(resource_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """删除酒店（管理员）"""
    service = ResourceService(db)
    resource = service.get_by_id(Hotel, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    service.delete(resource)

@router.delete("/restaurants/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(resource_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """删除餐厅（管理员）"""
    service = ResourceService(db)
    resource = service.get_by_id(Restaurant, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    service.delete(resource)


# 资源可用性查询
@router.get("/guides/available")
def get_available_guides(
    start: str = Query(..., description="开始时间 ISO 格式"),
    end: str = Query(..., description="结束时间 ISO 格式"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询指定时段内可用的导游"""
    service = ResourceService(db)
    conflict_service = ConflictService(db)
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    
    all_guides = service.get_guides()
    available = []
    for guide in all_guides:
        conflicts = conflict_service.check_resource_conflict("guide", guide.id, start_time, end_time)
        if not conflicts:
            available.append({"id": guide.id, "name": guide.name, "contact_phone": guide.contact_phone})
    return available

@router.get("/vehicles/available")
def get_available_vehicles(
    start: str = Query(..., description="开始时间 ISO 格式"),
    end: str = Query(..., description="结束时间 ISO 格式"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """查询指定时段内可用的车辆"""
    service = ResourceService(db)
    conflict_service = ConflictService(db)
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    
    all_vehicles = service.get_vehicles()
    available = []
    for vehicle in all_vehicles:
        conflicts = conflict_service.check_resource_conflict("vehicle", vehicle.id, start_time, end_time)
        if not conflicts:
            available.append({"id": vehicle.id, "name": vehicle.name, "plate_number": vehicle.plate_number, "seats": vehicle.seats})
    return available

@router.get("/{resource_type}/{resource_id}/schedule")
def get_resource_schedule(
    resource_type: str,
    resource_id: int,
    start: str = Query(..., description="开始时间 ISO 格式"),
    end: str = Query(..., description="结束时间 ISO 格式"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取资源在指定时间段内的占用情况"""
    if resource_type not in ["guide", "vehicle", "hotel", "restaurant"]:
        return {"error": "无效的资源类型"}
    
    conflict_service = ConflictService(db)
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    
    schedule = conflict_service.get_resource_schedule(resource_type, resource_id, start_time, end_time)
    return {"resource_type": resource_type, "resource_id": resource_id, "schedule": schedule}
