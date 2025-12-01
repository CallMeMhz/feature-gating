"""管理员路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime
from app.deps import get_db, get_current_admin
from app.schemas.user import UserCreate, UserResponse, PasswordChange
from app.services.auth import get_password_hash, verify_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """获取所有用户"""
    users = []
    async for user in db.users.find():
        users.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "created_by": user["created_by"]
        })
    return users


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """创建用户"""
    # 检查用户名是否已存在
    existing = await db.users.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    user = {
        "username": user_data.username,
        "hashed_password": get_password_hash(user_data.password),
        "role": user_data.role,
        "created_by": current_admin["username"],
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user)
    
    return {
        "id": str(result.inserted_id),
        "username": user["username"],
        "role": user["role"],
        "created_by": user["created_by"]
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """删除用户"""
    # 检查用户是否存在
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if str(user["_id"]) == str(current_admin["_id"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    await db.users.delete_one({"_id": ObjectId(user_id)})
    
    return {"message": "用户已删除"}


@router.put("/users/{user_id}/password")
async def change_password(
    user_id: str,
    password_data: PasswordChange,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_admin: dict = Depends(get_current_admin)
):
    """修改用户密码"""
    # 检查用户是否存在
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果是修改自己的密码，需要验证旧密码
    if str(user["_id"]) == str(current_admin["_id"]) and password_data.old_password:
        if not verify_password(password_data.old_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="旧密码不正确"
            )
    
    # 更新密码
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": get_password_hash(password_data.new_password)}}
    )
    
    return {"message": "密码已更新"}

