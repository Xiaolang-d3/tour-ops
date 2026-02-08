from sqlalchemy import Column, Integer, String, Date, Enum, DateTime, ForeignKey, JSON, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from TourOps.core.database import Base
import enum

class TripStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    guest_count = Column(Integer, default=1)
    budget = Column(DECIMAL(10, 2))
    preferences = Column(JSON)  # 偏好设置
    special_requirements = Column(JSON)  # 特殊需求
    status = Column(Enum(TripStatus), default=TripStatus.DRAFT)
    share_code = Column(String(32), unique=True, index=True)  # 分享码
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    activities = relationship("Activity", back_populates="trip", cascade="all, delete-orphan")
