from pydantic import BaseModel
from datetime import datetime
from TourOps.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    password: str
    name: str | None = None
    role: UserRole = UserRole.PLANNER

class ProfileUpdate(BaseModel):
    """用户可自行修改的资料"""
    name: str | None = None
    avatar: str | None = None

class UserResponse(BaseModel):
    id: int
    username: str
    name: str | None
    role: UserRole
    avatar: str | None = None
    created_at: datetime | None = None
    
    class Config:
        from_attributes = True

class RoleUpdate(BaseModel):
    """管理员修改用户角色"""
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str
