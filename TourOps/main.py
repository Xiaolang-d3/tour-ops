# -*- coding: utf-8 -*-
"""TourOps 主服务"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
def root():
    return {"service": "TourOps API", "version": "1.0"}