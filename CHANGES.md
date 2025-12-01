# 更新记录

## 重要改动

### 1. 前端构建系统

**使用 pnpm + Tailwind CLI**（不使用 Vite）：

**添加**：
- `app/package.json` - pnpm 配置
- `app/tailwind.config.js` - Tailwind 配置
- `app/src/styles.css` - 样式源码
- `app/static/app.js` - 自定义 JS

**构建产物**（输出到 `app/static/`）：
- `styles.css` - 编译后的 Tailwind CSS
- `alpine.min.js` - Alpine.js（从 node_modules 复制）
- `htmx.min.js` - htmx（从 node_modules 复制）

**使用方法**：
```bash
# 安装依赖
pnpm install

# 开发模式（监听 CSS 变化）
pnpm run css:dev

# 生产构建（编译 CSS + 复制库文件）
pnpm run build
```

### 2. 数据结构重构

**从独立 items 集合改为嵌入式结构**：

**之前**：
- `items` 独立集合，通过 `project_id` 关联
- 每个 item 单独增删改

**现在**：
- items 作为 projects 的嵌入数组字段
- 整体保存，通过右侧"保存更改"按钮提交

**优点**：
✅ 一次查询获取完整项目配置  
✅ 原子性更好，避免数据不一致  
✅ 更符合 UI 交互逻辑  
✅ 索引简单：在 `name` 和 `items.name` 上建立  

**数据结构**：
```json
{
  "_id": "...",
  "name": "main",
  "created_by": "admin",
  "created_at": "2025-12-01T00:00:00Z",
  "items": [
    {
      "name": "feature_x",
      "description": "...",
      "enabled": true,
      "conditions": [...]
    }
  ]
}
```

### 3. UI 改进

**修复的问题**：

1. ✅ **右侧边栏更窄**：从 `w-80` 改为 `w-64`
2. ✅ **Item 卡片响应式**：`grid-template-columns: repeat(auto-fill, minmax(320px, 1fr))`
3. ✅ **登录前 Projects 列表**：显示"请先登录"而不是"加载中"
4. ✅ **创建 Project 后刷新**：自动重新加载项目列表
5. ✅ **编辑自动点亮保存按钮**：所有输入都会触发 `markChanged()`
6. ✅ **删除走保存流程**：删除 item 只是本地操作，通过"保存更改"提交

### 4. API 调整

**删除的路由**：
- `/api/items` 系列接口（GET/POST/PUT/DELETE）

**新增的路由**：
- `PUT /api/projects/{id}` - 更新项目（包括 items）

**修改的路由**：
- `GET /api/projects` - 返回包含 items 数组
- `GET /api/projects/{id}` - 返回包含 items 数组

### 5. 代码清理

**删除的文件**：
- `app/routers/items.py`
- `app/models/item.py`
- `app/schemas/item.py`
- `vite.config.js`
- `frontend/` 目录（已移动到 `app/src/`）

**新增/调整**：
- `app/models/project.py` - 包含 ItemData 模型
- `app/schemas/project.py` - 包含 Item schema
- `app/src/styles.css` - Tailwind 源码
- `app/static/app.js` - 自定义 JS

## 迁移指南

如果您已经有数据，需要迁移：

```javascript
// MongoDB 迁移脚本
db.projects.find().forEach(project => {
    // 查找该项目的所有 items
    const items = db.items.find({project_id: project._id.toString()}).toArray();
    
    // 移除 project_id 字段
    items.forEach(item => {
        delete item._id;
        delete item.project_id;
    });
    
    // 更新项目，添加 items 数组
    db.projects.updateOne(
        {_id: project._id},
        {$set: {items: items}}
    );
});

// 确认无误后删除 items 集合
// db.items.drop();
```

## 启动流程

```bash
# 1. 安装 Python 依赖（使用 uv）
uv sync

# 2. 安装 pnpm 依赖
pnpm install

# 3. 构建前端资源
pnpm run build

# 4. 启动 MongoDB
docker-compose up -d

# 5. 启动应用
uv run uvicorn app.main:app --reload
```

开发时可以同时运行：
```bash
# 终端 1: 前端 CSS 监听模式
pnpm run css:dev

# 终端 2: 后端
uv run uvicorn app.main:app --reload
```
