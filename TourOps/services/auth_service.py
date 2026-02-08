"""认证服务"""
from sqlalchemy.orm import Session
from typing import Optional
from TourOps.models.user import User
from TourOps.schemas.user import UserCreate
from TourOps.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_in: UserCreate) -> User:
        user = User(
            username=user_in.username,
            password_hash=get_password_hash(user_in.password),
            name=user_in.name,
            role=user_in.role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    def create_token(self, user: User) -> str:
        return create_access_token(data={"sub": str(user.id), "role": user.role})
