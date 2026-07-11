# TourOps

面向旅行社的智能行程编排与资源调度系统，采用 Monorepo 统一管理 API 服务与 Web 应用。

## 项目结构

```text
tour-ops/
├── api-server/  # FastAPI 后端服务
└── web/         # Vue 前端应用
```

## 模块说明

- [`api-server/`](./api-server/)：行程、活动、资源、模板、认证与 AI 推荐等后端能力。
- [`web/`](./web/)：行程编排、订单与资源管理等前端界面。

各模块的依赖、配置与启动方式请参阅对应目录中的 README 和配置文件。

## 仓库迁移

本仓库由 `TourOps-api-server` 与 `TourOps-web` 合并而成，并保留两个源仓库的 Git 提交历史及 Web 功能分支。
