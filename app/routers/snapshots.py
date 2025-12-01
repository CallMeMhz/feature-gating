"""快照路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime
import yaml
from app.deps import get_db, get_current_user
from app.schemas.snapshot import SnapshotCreate, SnapshotResponse
from app.services.cache import invalidate_cache

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


async def generate_snapshot_yaml(db: AsyncIOMotorDatabase, project_id: str, remark: str = "", updated_by: str = "") -> str:
    """生成项目快照的 YAML"""
    # 获取项目信息
    project = await db.projects.find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 构建 YAML 数据（items 已经在 project 中）
    snapshot_data = {
        "snapshot": {
            "updated_by": updated_by,
            "remark": remark
        },
        "project": {
            "id": str(project["_id"]),
            "name": project["name"],
            "created_at": project["created_at"].isoformat()
        },
        "items": project.get("items", [])
    }
    
    return yaml.dump(snapshot_data, allow_unicode=True, sort_keys=False)


@router.get("/all")
async def get_all_snapshots(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取所有快照（用于管理员页面）"""
    snapshots = []
    async for snapshot in db.snapshots.find().sort("updated_at", -1):
        snapshots.append({
            "id": str(snapshot["_id"]),
            "project_id": snapshot["project_id"],
            "project_name": snapshot.get("project_name"),
            "yaml": snapshot["yaml"],
            "updated_by": snapshot["updated_by"],
            "updated_at": snapshot["updated_at"],
            "remark": snapshot.get("remark", "")
        })
    return snapshots


@router.get("", response_model=List[SnapshotResponse])
async def get_snapshots(
    project_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取项目的历史快照"""
    snapshots = []
    async for snapshot in db.snapshots.find({"project_id": project_id}).sort("updated_at", -1):
        snapshots.append({
            "id": str(snapshot["_id"]),
            "project_id": snapshot["project_id"],
            "yaml": snapshot["yaml"],
            "updated_by": snapshot["updated_by"],
            "updated_at": snapshot["updated_at"],
            "remark": snapshot.get("remark", "")
        })
    return snapshots


@router.get("/{snapshot_id}", response_model=SnapshotResponse)
async def get_snapshot(
    snapshot_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """获取特定快照详情"""
    snapshot = await db.snapshots.find_one({"_id": ObjectId(snapshot_id)})
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="快照不存在"
        )
    
    return {
        "id": str(snapshot["_id"]),
        "project_id": snapshot["project_id"],
        "yaml": snapshot["yaml"],
        "updated_by": snapshot["updated_by"],
        "updated_at": snapshot["updated_at"],
        "remark": snapshot.get("remark", "")
    }


@router.post("", response_model=SnapshotResponse)
async def create_snapshot(
    snapshot_data: SnapshotCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建快照"""
    # 生成 YAML（包含备注和操作者）
    yaml_content = await generate_snapshot_yaml(
        db, 
        snapshot_data.project_id,
        remark=snapshot_data.remark,
        updated_by=current_user["username"]
    )
    
    # 获取项目信息
    project = await db.projects.find_one({"_id": ObjectId(snapshot_data.project_id)})
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    snapshot = {
        "project_id": snapshot_data.project_id,
        "project_name": project["name"],  # 冗余保存项目名称
        "yaml": yaml_content,
        "updated_by": current_user["username"],
        "updated_at": datetime.utcnow(),
        "remark": snapshot_data.remark
    }
    
    result = await db.snapshots.insert_one(snapshot)
    snapshot["_id"] = result.inserted_id
    
    # 清除缓存
    if project:
        invalidate_cache(project["name"])
    
    return {
        "id": str(snapshot["_id"]),
        "project_id": snapshot["project_id"],
        "project_name": snapshot.get("project_name"),  # 包含项目名称
        "yaml": snapshot["yaml"],
        "updated_by": snapshot["updated_by"],
        "updated_at": snapshot["updated_at"],
        "remark": snapshot["remark"]
    }

