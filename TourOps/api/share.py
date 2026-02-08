"""分享 API - 二维码生成"""
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
from qrcode.constants import ERROR_CORRECT_M

from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user
from TourOps.models.user import User
from TourOps.models.trip import Trip

router = APIRouter()


def _verify_trip_ownership(trip_id: int, user: User, db: Session) -> Trip:
    """校验行程归属"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


@router.get("/{trip_id}/qrcode")
def generate_qrcode(
    trip_id: int,
    base_url: str = "http://localhost:3000",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成行程分享二维码（仅限自己的行程）"""
    trip = _verify_trip_ownership(trip_id, current_user, db)
    
    if not trip.share_code:
        raise HTTPException(status_code=400, detail="行程未生成分享码")
    
    # 生成分享链接
    share_url = f"{base_url}/share/{trip.share_code}"
    
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(share_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=trip_{trip_id}_qrcode.png"}
    )


@router.get("/{trip_id}/share-info")
def get_share_info(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取行程分享信息（仅限自己的行程）"""
    trip = _verify_trip_ownership(trip_id, current_user, db)
    
    return {
        "trip_id": trip.id,
        "trip_name": trip.name,
        "share_code": trip.share_code,
        "share_url": f"/share/{trip.share_code}" if trip.share_code else None
    }
