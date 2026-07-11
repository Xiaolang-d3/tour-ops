from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from TourOps.core.database import Base
import enum

class ActivityType(str, enum.Enum):
    TRANSPORT = "transport"  # 交通
    ATTRACTION = "attraction"  # 景点
    MEAL = "meal"  # 餐饮
    HOTEL = "hotel"  # 住宿
    FREE = "free"  # 自由活动

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    type = Column(Enum(ActivityType), nullable=False)
    name = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String(200))
    cost = Column(DECIMAL(10, 2))
    notes = Column(Text)
    sort_order = Column(Integer, default=0)
    
    # 资源关联
    guide_id = Column(Integer, ForeignKey("guides.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    
    trip = relationship("Trip", back_populates="activities")
