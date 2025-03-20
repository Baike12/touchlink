from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os

from src.core.services import ExportService
from src.core.models import ExportTask
from src.core.tasks.export_tasks import execute_export_task
from src.utils.exceptions import NotFoundException
from src.config.database import get_db
from src.utils.logger import setup_logger

# 创建路由
router = APIRouter(prefix="/exports", tags=["导出"])

# 创建日志记录器
logger = setup_logger("exports_api")


# 数据模型
class ExportTaskCreate(BaseModel):
    """创建导出任务请求"""
    name: str = Field(..., description="任务名称")
    type: str = Field(..., description="导出类型，支持excel和csv")
    config: Dict[str, Any] = Field(..., description="导出配置")
    analysis_task_id: Optional[str] = Field(None, description="分析任务ID")


class ExportTaskResponse(BaseModel):
    """导出任务响应"""
    id: str = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    type: str = Field(..., description="导出类型")
    status: str = Field(..., description="任务状态")
    result_path: Optional[str] = Field(None, description="结果路径")
    analysis_task_id: Optional[str] = Field(None, description="分析任务ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class ExportFileInfo(BaseModel):
    """导出文件信息"""
    name: str = Field(..., description="文件名")
    path: str = Field(..., description="文件路径")
    size: int = Field(..., description="文件大小")
    type: str = Field(..., description="文件类型")
    created_at: str = Field(..., description="创建时间")


# 路由定义
@router.post("/tasks", response_model=ExportTaskResponse)
async def create_export_task(task: ExportTaskCreate, db: Session = Depends(get_db)):
    """创建导出任务"""
    try:
        # 检查导出类型
        if task.type not in ["excel", "csv"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的导出类型: {task.type}"
            )
        
        # 创建任务
        # 注意：这里使用了硬编码的用户ID，实际应用中应该从认证信息中获取
        user_id = "00000000-0000-0000-0000-000000000000"
        
        export_task = ExportTask(
            user_id=user_id,
            name=task.name,
            type=task.type,
            config=task.config,
            status="pending",
            analysis_task_id=task.analysis_task_id
        )
        
        # 保存到数据库
        db.add(export_task)
        db.commit()
        db.refresh(export_task)
        
        # 异步执行任务
        execute_export_task.delay(export_task.id)
        
        # 返回响应
        return ExportTaskResponse(
            id=export_task.id,
            name=export_task.name,
            type=export_task.type,
            status=export_task.status,
            result_path=export_task.result_path,
            analysis_task_id=export_task.analysis_task_id,
            created_at=export_task.created_at.isoformat(),
            updated_at=export_task.updated_at.isoformat()
        )
    
    except Exception as e:
        logger.error(f"创建导出任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建导出任务失败: {str(e)}"
        )


@router.get("/tasks", response_model=List[ExportTaskResponse])
async def get_export_tasks(db: Session = Depends(get_db)):
    """获取所有导出任务"""
    try:
        # 注意：这里使用了硬编码的用户ID，实际应用中应该从认证信息中获取
        user_id = "00000000-0000-0000-0000-000000000000"
        
        # 查询任务
        tasks = db.query(ExportTask).filter(ExportTask.user_id == user_id).all()
        
        # 返回响应
        return [
            ExportTaskResponse(
                id=task.id,
                name=task.name,
                type=task.type,
                status=task.status,
                result_path=task.result_path,
                analysis_task_id=task.analysis_task_id,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]
    
    except Exception as e:
        logger.error(f"获取导出任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出任务列表失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=ExportTaskResponse)
async def get_export_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """获取导出任务详情"""
    try:
        # 查询任务
        task = db.query(ExportTask).filter(ExportTask.id == task_id).first()
        if not task:
            raise NotFoundException(f"导出任务不存在: {task_id}")
        
        # 返回响应
        return ExportTaskResponse(
            id=task.id,
            name=task.name,
            type=task.type,
            status=task.status,
            result_path=task.result_path,
            analysis_task_id=task.analysis_task_id,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取导出任务详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出任务详情失败: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """删除导出任务"""
    try:
        # 查询任务
        task = db.query(ExportTask).filter(ExportTask.id == task_id).first()
        if not task:
            raise NotFoundException(f"导出任务不存在: {task_id}")
        
        # 删除任务
        db.delete(task)
        db.commit()
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除导出任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除导出任务失败: {str(e)}"
        )


@router.get("/files", response_model=List[ExportFileInfo])
async def list_export_files():
    """列出所有导出文件"""
    try:
        # 获取文件列表
        files = ExportService.list_export_files()
        
        # 返回响应
        return files
    
    except Exception as e:
        logger.error(f"获取导出文件列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出文件列表失败: {str(e)}"
        )


@router.get("/files/{file_name}")
async def download_export_file(
    file_name: str = Path(..., description="文件名")
):
    """下载导出文件"""
    try:
        # 构建文件路径
        file_path = os.path.join(ExportService.EXPORT_DIR, file_name)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise NotFoundException(f"文件不存在: {file_name}")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=file_name,
            media_type="application/octet-stream"
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"下载文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


@router.delete("/files/{file_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_export_file(
    file_name: str = Path(..., description="文件名")
):
    """删除导出文件"""
    try:
        # 构建文件路径
        file_path = os.path.join(ExportService.EXPORT_DIR, file_name)
        
        # 删除文件
        ExportService.delete_export_file(file_path)
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {file_name}"
        )
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}"
        ) 