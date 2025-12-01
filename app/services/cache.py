"""内存缓存管理"""
from cachetools import TTLCache
from typing import Optional, Dict, Any
from app.config import get_settings

settings = get_settings()

# 创建 TTL 缓存
# maxsize: 最多缓存 1000 个项目
# ttl: 缓存过期时间（秒）
item_cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)


def get_cache_key(project_name: str, item_name: str) -> str:
    """生成缓存键"""
    return f"{project_name}:{item_name}"


def get_cached_item(project_name: str, item_name: str) -> Optional[Dict[str, Any]]:
    """从缓存获取 item"""
    key = get_cache_key(project_name, item_name)
    return item_cache.get(key)


def set_cached_item(project_name: str, item_name: str, item_data: Dict[str, Any]):
    """设置 item 到缓存"""
    key = get_cache_key(project_name, item_name)
    item_cache[key] = item_data


def invalidate_cache(project_name: str):
    """清除指定项目的所有缓存"""
    keys_to_delete = [key for key in item_cache.keys() if key.startswith(f"{project_name}:")]
    for key in keys_to_delete:
        del item_cache[key]


def clear_all_cache():
    """清除所有缓存"""
    item_cache.clear()

