"""资源服务"""
from sqlalchemy.orm import Session
from typing import List, Type, TypeVar
from TourOps.models.resource import Guide, Vehicle, Hotel, Restaurant
from TourOps.core.database import Base

T = TypeVar('T', bound=Base)

class ResourceService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, model: Type[T]) -> List[T]:
        return self.db.query(model).all()
    
    def get_by_id(self, model: Type[T], resource_id: int) -> T:
        return self.db.query(model).filter(model.id == resource_id).first()
    
    def create(self, model: Type[T], data: dict) -> T:
        resource = model(**data)
        self.db.add(resource)
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def update(self, resource: T, data: dict) -> T:
        for field, value in data.items():
            if value is not None:
                setattr(resource, field, value)
        self.db.commit()
        self.db.refresh(resource)
        return resource
    
    def delete(self, resource: T) -> None:
        self.db.delete(resource)
        self.db.commit()
    
    def get_guides(self) -> List[Guide]:
        return self.get_all(Guide)
    
    def get_vehicles(self) -> List[Vehicle]:
        return self.get_all(Vehicle)
    
    def get_hotels(self) -> List[Hotel]:
        return self.get_all(Hotel)
    
    def get_restaurants(self) -> List[Restaurant]:
        return self.get_all(Restaurant)
