from sqlalchemy import Column, Integer, String, JSON, DECIMAL
from TourOps.core.database import Base

class Resource(Base):
    """资源基类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    contact_phone = Column(String(20))
    tags = Column(JSON)  # 标签
    notes = Column(String(500))

class Guide(Resource):
    """导游"""
    __tablename__ = "guides"
    
    id_card = Column(String(20))  # 证件号
    languages = Column(JSON)  # 语言能力
    regions = Column(JSON)  # 擅长区域

class Vehicle(Resource):
    """车辆"""
    __tablename__ = "vehicles"
    
    plate_number = Column(String(20))  # 车牌号
    vehicle_type = Column(String(50))  # 车型
    seats = Column(Integer)  # 座位数
    driver_name = Column(String(50))
    driver_phone = Column(String(20))

class Hotel(Resource):
    """酒店"""
    __tablename__ = "hotels"
    
    address = Column(String(200))
    star_rating = Column(Integer)  # 星级
    room_types = Column(JSON)  # 房型与价格

class Restaurant(Resource):
    """餐厅"""
    __tablename__ = "restaurants"
    
    address = Column(String(200))
    cuisine = Column(String(50))  # 菜系
    price_min = Column(DECIMAL(10, 2))  # 餐标范围
    price_max = Column(DECIMAL(10, 2))
