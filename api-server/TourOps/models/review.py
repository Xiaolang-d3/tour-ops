"""行程评价模型"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Text
from sqlalchemy.sql import func
from TourOps.core.database import Base


class Review(Base):
    """行程评价"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id", ondelete="CASCADE"), nullable=False, index=True)
    share_code = Column(String(32), index=True)  # 通过分享码提交的评价
    rating = Column(Integer, nullable=False)  # 1-5 星级
    tags = Column(JSON)  # 评价标签列表，如 ["行程合理", "服务周到"]
    comment = Column(Text)  # 文字评价（选填）
    reviewer_name = Column(String(50))  # 评价人名称（选填，匿名时为空）
    created_at = Column(DateTime, server_default=func.now())
