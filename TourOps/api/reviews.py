"""评价 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user
from TourOps.models.user import User
from TourOps.models.trip import Trip
from TourOps.models.review import Review

router = APIRouter()


class ReviewCreate(BaseModel):
    rating: int  # 1-5
    tags: List[str] = []
    comment: str | None = None
    reviewer_name: str | None = None


class ReviewResponse(BaseModel):
    id: int
    trip_id: int
    rating: int
    tags: list | None
    comment: str | None
    reviewer_name: str | None
    created_at: str | None

    class Config:
        from_attributes = True


# ===== 公开接口：通过分享码提交评价 =====

@router.post("/public/trips/{share_code}/reviews")
def submit_public_review(share_code: str, review_in: ReviewCreate, db: Session = Depends(get_db)):
    """通过分享码提交评价（无需登录）"""
    trip = db.query(Trip).filter(Trip.share_code == share_code).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    if review_in.rating < 1 or review_in.rating > 5:
        raise HTTPException(status_code=400, detail="评分范围为1-5")

    review = Review(
        trip_id=trip.id,
        share_code=share_code,
        rating=review_in.rating,
        tags=review_in.tags,
        comment=review_in.comment or None,
        reviewer_name=review_in.reviewer_name or None,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"message": "评价提交成功", "id": review.id}


@router.get("/public/trips/{share_code}/reviews")
def get_public_reviews(share_code: str, db: Session = Depends(get_db)):
    """获取行程的公开评价列表"""
    trip = db.query(Trip).filter(Trip.share_code == share_code).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    reviews = db.query(Review).filter(Review.trip_id == trip.id).order_by(Review.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "rating": r.rating,
            "tags": r.tags or [],
            "comment": r.comment,
            "reviewer_name": r.reviewer_name or "匿名用户",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


# ===== 登录用户接口：查看自己行程的评价 =====

@router.get("/trips/{trip_id}/reviews")
def get_trip_reviews(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取行程评价列表"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    reviews = db.query(Review).filter(Review.trip_id == trip_id).order_by(Review.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "rating": r.rating,
            "tags": r.tags or [],
            "comment": r.comment,
            "reviewer_name": r.reviewer_name or "匿名用户",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]


@router.get("/trips/{trip_id}/reviews/stats")
def get_trip_review_stats(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取行程评价统计"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")

    reviews = db.query(Review).filter(Review.trip_id == trip_id).all()
    if not reviews:
        return {"total": 0, "avg_rating": 0, "rating_dist": {}, "tag_stats": {}}

    total = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total, 1)

    # 星级分布
    rating_dist = {}
    for i in range(1, 6):
        rating_dist[str(i)] = sum(1 for r in reviews if r.rating == i)

    # 标签统计
    tag_stats = {}
    for r in reviews:
        for tag in (r.tags or []):
            tag_stats[tag] = tag_stats.get(tag, 0) + 1

    return {
        "total": total,
        "avg_rating": avg_rating,
        "rating_dist": rating_dist,
        "tag_stats": tag_stats,
    }


# ===== 管理员接口：查看所有评价统计 =====

@router.get("/admin/reviews/stats")
def admin_review_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    """管理员查看全局评价统计"""
    from TourOps.api.deps import require_admin
    # 简单权限检查
    if admin.role.value != "admin":
        raise HTTPException(status_code=403, detail="无权限")

    reviews = db.query(Review).all()
    if not reviews:
        return {"total": 0, "avg_rating": 0, "rating_dist": {}, "tag_stats": {}, "recent": []}

    total = len(reviews)
    avg_rating = round(sum(r.rating for r in reviews) / total, 1)

    rating_dist = {}
    for i in range(1, 6):
        rating_dist[str(i)] = sum(1 for r in reviews if r.rating == i)

    tag_stats = {}
    for r in reviews:
        for tag in (r.tags or []):
            tag_stats[tag] = tag_stats.get(tag, 0) + 1

    # 最近10条
    recent = sorted(reviews, key=lambda r: r.created_at or "", reverse=True)[:10]
    recent_list = []
    for r in recent:
        trip = db.query(Trip).filter(Trip.id == r.trip_id).first()
        recent_list.append({
            "id": r.id,
            "trip_id": r.trip_id,
            "trip_name": trip.name if trip else "未知行程",
            "rating": r.rating,
            "tags": r.tags or [],
            "comment": r.comment,
            "reviewer_name": r.reviewer_name or "匿名用户",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "total": total,
        "avg_rating": avg_rating,
        "rating_dist": rating_dist,
        "tag_stats": tag_stats,
        "recent": recent_list,
    }
