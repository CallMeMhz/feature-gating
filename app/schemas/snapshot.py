"""快照 Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SnapshotCreate(BaseModel):
    """创建快照"""
    project_id: str
    remark: str = ""


class SnapshotResponse(BaseModel):
    """快照响应"""
    id: str
    project_id: str
    yaml: str
    updated_by: str
    updated_at: datetime
    remark: str
    
    class Config:
        from_attributes = True

