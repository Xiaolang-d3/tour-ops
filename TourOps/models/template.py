from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from TourOps.core.database import Base
import enum

class TemplateCategory(str, enum.Enum):
    FAMILY = "family"  # 亲子游
    BUSINESS = "business"  # 商务考察
    TEAM_BUILDING = "team_building"  # 团建
    ADVENTURE = "adventure"  # 探险游

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(Enum(TemplateCategory, values_callable=lambda x: [e.value for e in x]))
    duration_days = Column(Integer)  # 时长（天）
    content = Column(JSON)  # 模板内容
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
