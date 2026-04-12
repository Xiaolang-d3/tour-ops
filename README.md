# TourOps 后端服务

智能行程编排系统后端，基于 FastAPI 构建。

## 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                    TourOps API                          │
├─────────────────────────────────────────────────────────┤
│  公开接口（无需登录）                                    │
│  └─ GET /api/v1/public/trips/{share_code} 行程预览      │
├─────────────────────────────────────────────────────────┤
│  业务接口（计划员 + 管理员）                            │
│  ├─ 行程管理 /api/v1/trips                              │
│  ├─ 活动管理 /api/v1/trips/{id}/activities              │
│  └─ AI 推荐 /api/v1/ai/generate                         │
├─────────────────────────────────────────────────────────┤
│  管理接口（仅管理员）                                   │
│  ├─ 资源管理 /api/v1/resources                          │
│  └─ 模板管理 /api/v1/templates                          │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

- FastAPI 0.109.0
- SQLAlchemy 2.0 + PyMySQL
- Alembic 数据库迁移
- JWT 认证
- Pydantic 2.x

## Python 版本说明

- 推荐使用 Python 3.11.x
- 当前后端依赖已验证的范围是 Python 3.10-3.12
- 
## 项目结构

```
TourOps/
├── main.py             # 服务入口
├── api/                # 接口层 (Controller)
│   ├── auth.py         # 认证
│   ├── trips.py        # 行程
│   ├── activities.py   # 活动
│   ├── resources.py    # 资源（管理员）
│   ├── templates.py    # 模板（管理员）
│   ├── ai.py           # AI 推荐
│   └── public.py       # 公开接口
├── services/           # 业务逻辑层 (Service)
├── models/             # 数据模型
├── schemas/            # 数据验证
├── core/               # 核心模块
├── utils/              # 工具类
├── config/             # 配置文件
└── migrations/         # 数据库迁移
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置
copy TourOps\config\config.example.yaml TourOps\config\config.yaml

# 创建数据库
CREATE DATABASE TourOps CHARACTER SET utf8mb4;

# 生成迁移脚本（首次）
python -m TourOps.migrations.migrate revision "init"

# 初始化示例数据（可选）
python -m TourOps.migrations.seed

# 启动服务
uvicorn TourOps.main:app --reload
```

## 初始账号

- 用户名: `admin`
- 密码: `admin123`

## 用户角色

| 角色 | 权限 |
|------|------|
| admin | 全部功能 + 资源管理 + 模板管理 |
| planner | 行程管理 + 活动管理 + AI 推荐 |

## 配置文件

`TourOps/config/config.yaml`:

```yaml
database:
  host: localhost
  port: 3306
  user: root
  password: root
  name: TourOps

jwt:
  secret_key: your-secret-key
  algorithm: HS256
  expire_minutes: 1440

ai:
  api_key: your-api-key
  model: qwen-turbo
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
```

## API 文档

启动后访问: http://localhost:8000/docs
