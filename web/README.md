# TourOps Web

TourOps 前端项目，基于 Vue 3 + Vite + Element Plus，提供行程管理、模板管理、AI 推荐、公开分享页、管理员后台等功能。

## 技术栈

- Vue 3
- Vite 5
- Vue Router 4
- Pinia
- Element Plus
- Axios
- Sass

## 功能概览

- 登录/注册与基于角色的页面访问控制（`admin` / `planner`）
- 行程列表与行程详情管理
- 模板管理
- AI 行程推荐
- 公开分享页（含合作伙伴确认与评价）
- 管理员后台（用户、行程、资源、模板、评价）

## 本地开发

### 环境要求

- Node.js 18+（推荐 Node.js 20 LTS）
- npm 9+

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

默认启动地址：`http://localhost:3000`

## 后端联调说明

- 前端请求基地址是 `/api/v1`
- Vite 开发代理会将 `/api` 转发到 `http://localhost:8000`
- 请先启动后端服务，再启动前端

后端默认管理员账号（由后端迁移脚本初始化）：

- 用户名：`admin`
- 密码：`admin123`

## 生产构建

```bash
npm run build
```

构建产物目录：`dist/`

本地预览构建结果：

```bash
npm run preview
```

## 可用脚本

- `npm run dev`：启动开发环境
- `npm run build`：打包生产版本
- `npm run preview`：预览生产构建

## 目录结构

```text
src/
├── api/            # 接口请求封装
├── layout/         # 页面布局（管理端/业务端）
├── router/         # 路由与权限守卫
├── stores/         # Pinia 状态管理
├── styles/         # 全局样式
├── utils/          # 通用工具（如 request 封装）
└── views/          # 页面视图
```

## 注意事项

- 当前项目未配置自动化测试。
- 登录态 token 保存在 `localStorage`，401 时会自动清理并跳转到登录页。
