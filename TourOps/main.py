# -*- coding: utf-8 -*-
"""TourOps 主服务"""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from TourOps.core.config import settings
from TourOps.api import api_router
from TourOps.migrations.migrate import upgrade

# 启动时自动迁移数据库
upgrade()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="行程编排系统 API",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

# 前端静态文件服务
STATIC_DIR = Path(__file__).parent.parent.parent / "TourOps-web" / "dist"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        """所有非 API 路径返回前端 index.html（SPA 路由支持）"""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    def root():
        return {"service": "TourOps API", "version": "1.0"}