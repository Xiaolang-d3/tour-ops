"""导出 API - PDF/Excel 行程单"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from TourOps.core.database import get_db
from TourOps.api.deps import get_current_user
from TourOps.models.user import User
from TourOps.models.trip import Trip
from TourOps.services.export_service import ExportService

router = APIRouter()


def _verify_trip_ownership(trip_id: int, user: User, db: Session) -> Trip:
    """校验行程归属"""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.created_by == user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="行程不存在")
    return trip


@router.get("/{trip_id}/export/pdf")
def export_trip_pdf(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出行程 PDF（仅限自己的行程）"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ExportService(db)
    try:
        pdf_buffer = service.generate_pdf(trip_id)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {str(e)}")


@router.get("/{trip_id}/export/excel")
def export_trip_excel(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出行程 Excel（仅限自己的行程）"""
    _verify_trip_ownership(trip_id, current_user, db)
    service = ExportService(db)
    try:
        excel_buffer = service.generate_excel(trip_id)
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=trip_{trip_id}.xlsx"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel 生成失败: {str(e)}")
