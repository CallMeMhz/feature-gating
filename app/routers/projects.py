"""项目路由"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime
from app.deps import get_db, get_current_user, get_current_admin
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.cache import invalidate_cache

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取所有项目"""
    projects = []
    async for project in db.projects.find():
        projects.append({
            "id": str(project["_id"]),
            "name": project["name"],
            "created_by": project["created_by"],
            "created_at": project["created_at"],
            "items": project.get("items", [])
        })
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取单个项目"""
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "created_by": project["created_by"],
        "created_at": project["created_at"],
        "items": project.get("items", [])
    }


@router.post("")
async def create_project(
    request: Request,
    project_data: ProjectCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建项目"""
    # 检查项目名是否已存在
    existing = await db.projects.find_one({"name": project_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="项目名称已存在"
        )
    
    project = {
        "name": project_data.name,
        "created_by": current_user["username"],
        "created_at": datetime.utcnow(),
        "items": []
    }
    
    result = await db.projects.insert_one(project)
    project["_id"] = result.inserted_id
    
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "created_by": project["created_by"],
        "created_at": project["created_at"].isoformat(),
        "items": []
    }


@router.put("/{project_id}")
async def update_project(
    request: Request,
    project_id: str,
    project_data: ProjectUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """更新项目（包括 items）"""
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    import re
    from collections import Counter
    
    # 检查是否有空的 item name
    empty_items = [i for i, item in enumerate(project_data.items) if not item.name or not item.name.strip()]
    if empty_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"第 {', '.join(str(i+1) for i in empty_items)} 个 Item 的 Key 不能为空"
        )
    
    # 检查 Key 格式（允许：小写字母、数字、-_.$#@）
    key_pattern = re.compile(r'^[a-z0-9_.\-#$@]+$')
    invalid_items = [
        (i, item.name.strip()) 
        for i, item in enumerate(project_data.items) 
        if not key_pattern.match(item.name.strip())
    ]
    if invalid_items:
        invalid_names = [f"'{name}' (第{i+1}个)" for i, name in invalid_items]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Key 格式不正确: {', '.join(invalid_names)}。只能包含小写字母、数字、-_.$#@"
        )
    
    # 检查是否有重复的 item name（大小写不敏感）
    item_names = [item.name.strip().lower() for item in project_data.items]
    if len(item_names) != len(set(item_names)):
        # 找出重复的名称
        duplicates = [name for name, count in Counter(item_names).items() if count > 1]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"存在重复的 Key（大小写不敏感）: {', '.join(duplicates)}"
        )
    
    # 将 Pydantic 对象转换为字典
    items_dict = [item.model_dump() for item in project_data.items]
    
    # 更新整个项目（包括 items）
    await db.projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"items": items_dict}}
    )
    
    # 清除缓存
    invalidate_cache(project["name"])
    
    updated_project = await db.projects.find_one({"_id": ObjectId(project_id)})
    
    return {
        "id": str(updated_project["_id"]),
        "name": updated_project["name"],
        "created_by": updated_project["created_by"],
        "created_at": updated_project["created_at"].isoformat(),
        "items": updated_project.get("items", [])
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_admin)  # 只有管理员可以删除项目
):
    """删除项目（仅管理员）"""
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 删除项目（items 会一起删除）
    await db.projects.delete_one({"_id": ObjectId(project_id)})
    
    # 清除缓存
    invalidate_cache(project["name"])
    
    return {"message": "项目已删除"}
