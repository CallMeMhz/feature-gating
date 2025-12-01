"""项目 Schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Condition(BaseModel):
    """条件"""
    field: str
    operator: str
    value: int
    comparator: str
    target: int


class Item(BaseModel):
    """Item"""
    name: str
    description: str = ""
    enabled: bool = True
    conditions: List[Condition] = []


class ProjectCreate(BaseModel):
    """创建项目"""
    name: str


class ProjectUpdate(BaseModel):
    """更新项目"""
    items: List[Item]


class ProjectResponse(BaseModel):
    """项目响应"""
    id: str
    name: str
    created_by: str
    created_at: datetime
    items: List[Item] = []
    
    class Config:
        from_attributes = True
