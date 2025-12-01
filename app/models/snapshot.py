"""快照模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class SnapshotModel(BaseModel):
    """快照数据模型"""
    id: Optional[str] = Field(default=None, alias="_id")
    project_id: str
    yaml: str
    updated_by: str
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    remark: str = ""
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

