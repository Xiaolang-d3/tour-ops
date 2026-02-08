from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from TourOps.core.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    PLANNER = "planner"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.PLANNER)
    avatar = Column(String(50), nullable=True)  # 预设头像标识，如 "gradient-1" 或 emoji
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
