"""MongoDB 数据库连接管理"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()

# MongoDB 客户端
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """连接到 MongoDB"""
    global client, db
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client.get_database()
    print(f"Connected to MongoDB: {settings.mongo_url}")


async def close_mongo_connection():
    """关闭 MongoDB 连接"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


def get_database() -> AsyncIOMotorDatabase:
    """获取数据库实例"""
    return db

