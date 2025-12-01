"""用户 Schemas"""
from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    """创建用户"""
    username: str
    password: str
    role: str = "user"


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    role: str
    created_by: str
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"


class PasswordChange(BaseModel):
    """修改密码"""
    old_password: Optional[str] = None
    new_password: str

