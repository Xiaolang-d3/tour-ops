from fastapi import APIRouter
from TourOps.api import auth, trips, activities, resources, templates, ai, public, export, share

api_router = APIRouter()

# 公开接口（无需登录）
api_router.include_router(public.router, prefix="/public", tags=["公开接口"])

# 认证接口
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 业务接口（计划员 + 管理员）
api_router.include_router(trips.router, prefix="/trips", tags=["行程管理"])
api_router.include_router(activities.router, prefix="/trips", tags=["活动管理"])
api_router.include_router(export.router, prefix="/trips", tags=["导出"])
api_router.include_router(share.router, prefix="/trips", tags=["分享"])
api_router.include_router(ai.router, prefix="/ai", tags=["智能推荐"])

# 管理接口（仅管理员）
api_router.include_router(resources.router, prefix="/resources", tags=["资源管理"])
api_router.include_router(templates.router, prefix="/templates", tags=["模板管理"])
