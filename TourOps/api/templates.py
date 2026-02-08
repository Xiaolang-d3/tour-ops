from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, date, timedelta
import secrets
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user, require_admin
from TourOps.models.user import User
from TourOps.models.template import Template, TemplateCategory
from TourOps.models.trip import Trip, TripStatus
from TourOps.models.activity import Activity, ActivityType

router = APIRouter()

class TemplateCreate(BaseModel):
    name: str
    category: TemplateCategory
    duration_days: int
    content: dict

class TemplateUpdate(BaseModel):
    name: str | None = None
    category: TemplateCategory | None = None
    duration_days: int | None = None
    content: dict | None = None

class TemplateResponse(BaseModel):
    id: int
    name: str
    category: TemplateCategory
    duration_days: int
    content: dict | None
    created_by: int | None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("", response_model=List[TemplateResponse])
def list_templates(category: TemplateCategory | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取模板列表"""
    query = db.query(Template)
    if category:
        query = query.filter(Template.category == category)
    return query.all()

@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(template_in: TemplateCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """创建模板（管理员）"""
    template = Template(**template_in.model_dump(), created_by=admin.id)
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取模板详情"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template

@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template_in: TemplateUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """更新模板（管理员）"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    for field, value in template_in.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return template

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(template_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """删除模板（管理员）"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    db.delete(template)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

class TripToTemplateRequest(BaseModel):
    name: str
    category: TemplateCategory

@router.post("/from-trip/{trip_id}", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template_from_trip(
    trip_id: int,
    request: TripToTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从行程创建模板（仅限自己的行程）"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    
    activities = db.query(Activity).filter(Activity.trip_id == trip_id).order_by(Activity.sort_order, Activity.start_time).all()
    
    # 构建模板内容
    duration_days = (trip.end_date - trip.start_date).days + 1
    content = {
        "activities": [
            {
                "day": (act.start_time.date() - trip.start_date).days + 1,
                "type": act.type.value,
                "name": act.name,
                "start_time": act.start_time.strftime("%H:%M"),
                "end_time": act.end_time.strftime("%H:%M"),
                "duration_hours": (act.end_time - act.start_time).seconds / 3600,
                "location": act.location,
                "cost": float(act.cost) if act.cost else None,
                "notes": act.notes
            }
            for act in activities
        ],
        "guest_count": trip.guest_count,
        "budget": float(trip.budget) if trip.budget else None,
        "preferences": trip.preferences,
        "special_requirements": trip.special_requirements
    }
    
    template = Template(
        name=request.name,
        category=request.category,
        duration_days=duration_days,
        content=content,
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


class CreateTripFromTemplateRequest(BaseModel):
    name: str
    start_date: date
    guest_count: int | None = None
    budget: float | None = None


@router.post("/{template_id}/create-trip", status_code=status.HTTP_201_CREATED)
def create_trip_from_template(
    template_id: int,
    request: CreateTripFromTemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从模板创建行程"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 确保 content 是字典（防止双重序列化的 JSON 字符串）
    import json
    content = template.content
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            content = {}
    if not isinstance(content, dict):
        content = {}

    # 计算结束日期
    duration_days = template.duration_days or 1
    end_date = request.start_date + timedelta(days=duration_days - 1)

    # 检测日期冲突
    conflicts = db.query(Trip).filter(
        Trip.created_by == current_user.id,
        Trip.status.notin_([TripStatus.CANCELLED]),
        Trip.start_date <= end_date,
        Trip.end_date >= request.start_date,
    ).all()
    if conflicts:
        names = "、".join(f"「{t.name}」({t.start_date} ~ {t.end_date})" for t in conflicts)
        raise HTTPException(
            status_code=409,
            detail=f"该时间段与已有行程存在冲突：{names}，同一时间段只能有一个行程。"
        )

    # 创建行程（用户传入的值优先，否则用模板中保存的值）
    trip = Trip(
        name=request.name,
        start_date=request.start_date,
        end_date=end_date,
        guest_count=request.guest_count if request.guest_count is not None else (content.get("guest_count", 1) if content else 1),
        budget=request.budget if request.budget is not None else (content.get("budget") if content else None),
        preferences=content.get("preferences") if content else None,
        special_requirements=content.get("special_requirements") if content else None,
        share_code=secrets.token_hex(16),
        created_by=current_user.id,
    )
    db.add(trip)
    db.flush()

    # 映射活动类型（支持中英文）
    type_map = {
        "transport": ActivityType.TRANSPORT,
        "attraction": ActivityType.ATTRACTION,
        "meal": ActivityType.MEAL,
        "hotel": ActivityType.HOTEL,
        "free": ActivityType.FREE,
        "交通": ActivityType.TRANSPORT,
        "景点": ActivityType.ATTRACTION,
        "餐饮": ActivityType.MEAL,
        "住宿": ActivityType.HOTEL,
        "自由活动": ActivityType.FREE,
        "自由": ActivityType.FREE,
    }

    # 根据模板内容创建活动
    activity_count = 0
    activities_data = content.get("activities", []) if content else []
    if not isinstance(activities_data, list):
        activities_data = []

    for idx, act_data in enumerate(activities_data):
        try:
            if not isinstance(act_data, dict):
                continue

            day = int(act_data.get("day", 1))
            # 确保 day 在合理范围内
            if day < 1:
                day = 1
            if day > duration_days:
                day = duration_days
            act_date = request.start_date + timedelta(days=day - 1)

            # 解析开始时间
            start_time_str = act_data.get("start_time") or act_data.get("time") or "09:00"
            try:
                parts = str(start_time_str).split(":")
                hour = int(parts[0]) % 24
                minute = int(parts[1]) % 60 if len(parts) > 1 else 0
            except (ValueError, AttributeError, IndexError):
                hour, minute = 9, 0

            start_dt = datetime(act_date.year, act_date.month, act_date.day, hour, minute)

            # 解析结束时间：优先用 end_time，否则用 duration_hours / duration
            end_dt = None
            if act_data.get("end_time"):
                try:
                    end_parts = str(act_data["end_time"]).split(":")
                    end_hour = int(end_parts[0]) % 24
                    end_minute = int(end_parts[1]) % 60 if len(end_parts) > 1 else 0
                    end_dt = datetime(act_date.year, act_date.month, act_date.day, end_hour, end_minute)
                    if end_dt <= start_dt:
                        end_dt = start_dt + timedelta(hours=2)
                except (ValueError, AttributeError, IndexError):
                    pass

            if end_dt is None:
                duration_hours = act_data.get("duration_hours") or act_data.get("duration", 2)
                try:
                    # duration 可能是 "2小时" 之类的字符串
                    if isinstance(duration_hours, str):
                        duration_hours = float(''.join(c for c in duration_hours if c.isdigit() or c == '.') or '2')
                    duration_hours = float(duration_hours)
                    if duration_hours <= 0:
                        duration_hours = 2
                except (ValueError, TypeError):
                    duration_hours = 2
                end_dt = start_dt + timedelta(hours=duration_hours)

            # 映射活动类型
            act_type = type_map.get(act_data.get("type", "attraction"), ActivityType.ATTRACTION)

            # 解析费用
            cost = None
            if act_data.get("cost") is not None or act_data.get("estimated_cost") is not None:
                try:
                    cost = float(act_data.get("cost") or act_data.get("estimated_cost") or 0)
                except (ValueError, TypeError):
                    cost = None

            activity = Activity(
                trip_id=trip.id,
                type=act_type,
                name=act_data.get("name", "未命名活动"),
                start_time=start_dt,
                end_time=end_dt,
                location=act_data.get("location"),
                cost=cost,
                notes=act_data.get("notes"),
                sort_order=idx,
            )
            db.add(activity)
            activity_count += 1
        except Exception as e:
            # 单个活动创建失败不影响其他活动
            print(f"[create_trip_from_template] 跳过活动 {idx}: {e}")
            continue

    db.commit()
    db.refresh(trip)
    return {
        "id": trip.id,
        "name": trip.name,
        "start_date": str(trip.start_date),
        "end_date": str(trip.end_date),
        "status": trip.status.value,
        "activity_count": activity_count,
    }
