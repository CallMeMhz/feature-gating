"""项目模型"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class ItemData(BaseModel):
    """Item 数据（嵌入在 Project 中）"""
    name: str
    description: str = ""
    enabled: bool = True
    conditions: List[dict] = []


class ProjectModel(BaseModel):
    """项目数据模型"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    items: List[ItemData] = []  # 嵌入的 items 数组
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

