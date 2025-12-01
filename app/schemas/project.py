"""项目 Schemas"""
from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime


class Condition(BaseModel):
    """条件"""
    field: str
    operator: str
    value: Union[int, str, List[str]]  # 支持数字、字符串、字符串数组
    comparator: Optional[str] = None  # 对于白名单操作符，comparator 可选
    target: Optional[Union[int, str]] = None  # 对于白名单操作符，target 可选


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
