# Wawa - Feature Gating 管理系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

基于业务字段表达式的 Web 端功能控制平台，可以根据业务字段参与的表达式进行功能灰度控制。

## 功能特性

- 🎯 **灵活的条件表达式**: 支持哈希灰度 + 白名单/黑名单机制
- 📊 **多项目管理**: 支持多个项目，每个项目可包含多个功能项
- 🔐 **用户权限控制**: 基于 JWT 的认证系统，支持普通用户和管理员角色
- 💾 **配置快照**: 每次保存自动创建 YAML 快照，支持查看历史记录
- ⚡ **高性能缓存**: 内存缓存支持，可配置缓存过期时间
- 🐳 **Docker 支持**: 一条命令启动完整应用栈
- 🌐 **现代化 UI**: 基于 Tailwind CSS + htmx + Alpine.js 的响应式界面

> 📖 **快速开始？** 查看 [QUICKSTART.md](QUICKSTART.md) 30 秒启动应用

## 技术栈

### 后端
- **FastAPI**: 现代化的 Python Web 框架
- **MongoDB**: 文档型数据库，使用 Motor 异步驱动
- **JWT**: 基于 Token 的认证系统
- **PyYAML**: 配置快照生成

### 前端
- **Tailwind CSS 4**: 实用优先的 CSS 框架
- **htmx 2**: 现代化的 AJAX 交互
- **Alpine.js 3**: 轻量级的 JavaScript 框架

## 快速开始

### 🐳 方式 1：Docker Compose（推荐）

最简单的启动方式，一条命令搞定：

```bash
# 启动所有服务（MongoDB + 应用）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

访问应用：http://localhost:8000

默认管理员账号：
- 用户名：`admin`
- 密码：`admin`

⚠️ **生产环境请务必修改默认密码和密钥！** 详见 [DOCKER.md](DOCKER.md)

---

### 💻 方式 2：本地开发

#### 1. 环境要求

- Python 3.10+
- MongoDB 4.0+
- [uv](https://docs.astral.sh/uv/) - Python 包管理工具
- pnpm (或 npm)

#### 2. 安装依赖

```bash
# Python 依赖（uv 会自动创建虚拟环境）
uv sync

# 前端依赖
pnpm install
```

#### 3. 构建前端资源

```bash
pnpm run build
```

这会：
- 编译 Tailwind CSS
- 复制 Alpine.js、htmx 到 static 目录

#### 4. 配置环境变量

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件
vim .env
```

示例配置：

```env
# 应用配置
APP_TITLE=Feature Gating

# MongoDB 配置
MONGO_URL=mongodb://localhost:27017/wawa-fg

# 初始管理员账户（首次启动时创建）
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me_please

# JWT 密钥（使用: openssl rand -hex 32 生成）
JWT_SECRET_KEY=your-secret-key-here-change-in-production

# 缓存配置
CACHE_TTL_SECONDS=60
```

#### 5. 启动 MongoDB

使用 Docker Compose（仅启动 MongoDB）：

```bash
docker-compose up -d mongodb
```

或者使用本地 MongoDB 服务。

#### 6. 运行应用

```bash
# 使用 uv 运行
uv run uvicorn app.main:app --reload --port 8000

# 或者先激活虚拟环境
source .venv/bin/activate  # macOS/Linux
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000

## 开发模式

同时运行两个终端：

```bash
# 终端 1: CSS 自动编译（监听变化）
pnpm run css:dev

# 终端 2: FastAPI 热重载
uv run uvicorn app.main:app --reload
```

## API 使用示例

### Feature Gate 查询接口

检查功能是否对特定用户生效：

```bash
# GET 请求
curl "http://localhost:8000/api/fg/check?project=main&key=new_chat_ui&user_id=550e8400-e29b-41d4-a716-446655440000"

# POST 请求
curl -X POST "http://localhost:8000/api/fg/check" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "main",
    "key": "new_chat_ui",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "chat_id": "chat_123"
  }'
```

响应示例：

```json
{
  "enabled": true,
  "key": "new_chat_ui"
}
```

## 数据结构

### 项目（嵌入式结构）

```json
{
  "_id": "ObjectId",
  "name": "main",
  "created_by": "admin",
  "created_at": "2025-12-01T00:00:00Z",
  "items": [
    {
      "name": "new_chat_ui",
      "description": "新版聊天界面",
      "enabled": true,
      "conditions": [
        {
          "field": "user_id",
          "operator": "%",
          "value": 10,
          "comparator": "<",
          "target": 2
        }
      ]
    }
  ]
}
```

### 条件表达式

计算逻辑：`hash(field) operator value comparator target`

例如：`hash(user_id) % 10 < 2` 表示对 user_id 进行哈希后取模 10，如果小于 2 则通过（20% 用户）

### 支持的字段

- `user_id`: UUID v4 格式的用户 ID
- `chat_id`: 聊天 ID

### 支持的运算符

- `%`: 取模
- `/`: 除法
- `//`: 整除
- `*`: 乘法

### 支持的比较符

- `>`: 大于
- `<`: 小于
- `>=`: 大于等于
- `<=`: 小于等于
- `==`: 等于
- `!=`: 不等于

## 项目结构

```
wawa-fg/
├── app/
│   ├── main.py             # FastAPI 应用入口
│   ├── config.py           # 配置管理
│   ├── database.py         # MongoDB 连接
│   ├── deps.py             # 依赖注入
│   ├── models/             # 数据模型
│   ├── schemas/            # Pydantic Schemas
│   ├── routers/            # API 路由
│   ├── services/           # 业务逻辑
│   ├── templates/          # Jinja2 模板
│   ├── static/             # 静态资源（构建产物）
│   │   ├── styles.css      # 编译后的 CSS
│   │   ├── alpine.min.js
│   │   ├── htmx.min.js
│   │   └── app.js          # 自定义 JS
│   ├── src/                # 前端源码
│   │   └── styles.css      # Tailwind 源码
│   ├── package.json        # pnpm 配置
│   └── tailwind.config.js  # Tailwind 配置
├── docker-compose.yml      # Docker Compose 配置
└── pyproject.toml          # Python 配置
```

## 使用指南

### 1. 登录系统

使用初始管理员账户登录（在 `.env` 中配置）。

### 2. 创建项目

在左侧导航栏点击 "+" 按钮创建新项目。

### 3. 添加功能项（Item）

选择项目后，在主区域点击 "新增 Item" 按钮。

### 4. 配置条件

为 Item 添加灰度条件，例如：
- **20% 用户**: `hash(user_id) % 10 < 2`
- **50% 用户**: `hash(user_id) % 10 < 5`

### 5. 保存配置

点击右侧边栏的 "保存更改" 按钮，系统会自动创建配置快照。

### 6. 管理用户

管理员可访问 `/admin` 页面管理用户账户。

## 缓存机制

系统使用内存缓存优化查询性能：

- 缓存 key: `{project_name}:{item_name}`
- 缓存时间: 由 `CACHE_TTL_SECONDS` 环境变量控制（默认 60 秒）
- 自动失效: 配置更新时自动清除相关缓存

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

您可以自由地：
- ✅ 使用本软件进行商业用途
- ✅ 修改源代码
- ✅ 分发副本
- ✅ 私有使用

唯一要求是在副本中包含版权声明和许可声明。

## 贡献

欢迎提交 Issue 和 Pull Request！

在提交 PR 前，请确保：
- 代码风格一致
- 添加必要的测试
- 更新相关文档
