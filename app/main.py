"""FastAPI 应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import auth, projects, snapshots, admin, fg, pages
from app.services.auth import get_password_hash
from app.config import get_settings
from datetime import datetime

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await connect_to_mongo()
    await init_admin_user()
    yield
    # 关闭时
    await close_mongo_connection()


app = FastAPI(
    title=f"{settings.app_title}",
    description="基于业务字段表达式的功能控制平台",
    version="0.1.0",
    lifespan=lifespan
)

# 添加 Session 中间件（用于 flash messages）
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 注册路由
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(snapshots.router)
app.include_router(admin.router)
app.include_router(fg.router)


async def init_admin_user():
    """初始化管理员用户"""
    db = get_database()
    
    # 检查是否已有用户
    user_count = await db.users.count_documents({})
    if user_count == 0:
        # 创建初始管理员
        admin_user = {
            "username": settings.admin_username,
            "hashed_password": get_password_hash(settings.admin_password),
            "role": "admin",
            "created_by": "system",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(admin_user)
        print(f"创建初始管理员用户: {settings.admin_username}")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

