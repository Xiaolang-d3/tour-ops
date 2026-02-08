from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from TourOps.core.database import get_db
from typing import List
from TourOps.schemas.user import UserCreate, UserResponse, Token, LoginRequest, ProfileUpdate, RoleUpdate
from TourOps.services.auth_service import AuthService
from TourOps.api.deps import get_current_user, require_admin
from TourOps.models.user import User, UserRole
from TourOps.models.trip import Trip
from TourOps.models.activity import Activity
from TourOps.models.template import Template

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    公开注册接口 - 只允许注册 planner 角色。
    如果提交了 admin 角色，自动降级为 planner。
    """
    service = AuthService(db)
    if service.get_user_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    # 公开注册强制为 planner，防止权限提升
    user_in.role = UserRole.PLANNER
    user = service.create_user(user_in)
    return user


@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """
    管理员创建用户 - 可以指定任意角色（包括 admin）。
    """
    service = AuthService(db)
    if service.get_user_by_username(user_in.username):
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = service.create_user(user_in)
    return user


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    service = AuthService(db)
    user = service.authenticate(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access_token = service.create_token(user)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新个人资料（昵称、头像）"""
    if profile_in.name is not None:
        current_user.name = profile_in.name
    if profile_in.avatar is not None:
        current_user.avatar = profile_in.avatar
    db.commit()
    db.refresh(current_user)
    return current_user


# ==================== 管理员接口 ====================

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    """获取所有用户列表（管理员）"""
    users = db.query(User).order_by(User.id).all()
    return users


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """修改用户角色（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")
    user.role = role_in.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    force: bool = Query(False, description="强制删除，同时删除该用户的所有行程和模板"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除用户（管理员）。如果用户有关联数据，需要 force=true 才能删除。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    # 检查关联数据
    trip_count = db.query(Trip).filter(Trip.created_by == user_id).count()
    template_count = db.query(Template).filter(Template.created_by == user_id).count()

    if (trip_count > 0 or template_count > 0) and not force:
        raise HTTPException(
            status_code=409,
            detail=f"该用户有 {trip_count} 个行程和 {template_count} 个模板，"
                   f"请使用强制删除（force=true）以同时删除所有关联数据"
        )

    # 级联删除：先用原生 SQL 删除 activities 和 trips，避免 ORM flush 顺序问题
    user_trip_ids = [t.id for t in db.query(Trip.id).filter(Trip.created_by == user_id).all()]
    if user_trip_ids:
        db.query(Activity).filter(Activity.trip_id.in_(user_trip_ids)).delete(synchronize_session=False)
        db.query(Trip).filter(Trip.id.in_(user_trip_ids)).delete(synchronize_session=False)

    db.query(Template).filter(Template.created_by == user_id).delete(synchronize_session=False)

    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()
