from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.src.core.services import AnalyticsService
from backend.src.core.analytics import Pipeline, OperatorFactory
from backend.src.core.tasks import execute_analysis_task
from backend.src.core.tasks.task_logger import get_task_logger
from backend.src.utils.exceptions import AnalyticsException, NotFoundException
from backend.src.config.database import get_db
from backend.src.utils.logger import setup_logger

# 创建路由
router = APIRouter(prefix="/analytics", tags=["分析"])

# 创建日志记录器
logger = setup_logger("analytics_api")


# 数据模型
class OperatorInfo(BaseModel):
    """操作信息"""
    name: str = Field(..., description="操作名称")
    display_name: str = Field(..., description="显示名称")
    description: str = Field(..., description="描述")
    params: List[Dict[str, Any]] = Field(..., description="参数列表")


class PipelineStep(BaseModel):
    """流水线步骤"""
    id: Optional[str] = Field(None, description="步骤ID")
    operator_type: str = Field(..., description="操作类型")
    params: Dict[str, Any] = Field(..., description="操作参数")


class PipelineCreate(BaseModel):
    """创建流水线请求"""
    name: str = Field(..., description="流水线名称")
    description: Optional[str] = Field(None, description="流水线描述")
    steps: List[PipelineStep] = Field(..., description="流水线步骤")


class PipelineResponse(BaseModel):
    """流水线响应"""
    id: str = Field(..., description="流水线ID")
    name: str = Field(..., description="流水线名称")
    description: Optional[str] = Field(None, description="流水线描述")
    steps: List[PipelineStep] = Field(..., description="流水线步骤")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class TaskCreate(BaseModel):
    """创建任务请求"""
    name: str = Field(..., description="任务名称")
    pipeline: PipelineCreate = Field(..., description="分析流水线")
    datasource_id: Optional[str] = Field(None, description="数据源ID")


class TaskResponse(BaseModel):
    """任务响应"""
    id: str = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    status: str = Field(..., description="任务状态")
    pipeline: PipelineResponse = Field(..., description="分析流水线")
    datasource_id: Optional[str] = Field(None, description="数据源ID")
    result_path: Optional[str] = Field(None, description="结果路径")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: Optional[str] = Field(None, description="消息")


class TaskLogResponse(BaseModel):
    """任务日志响应"""
    id: str = Field(..., description="任务ID")
    logs: str = Field(..., description="日志内容")


# 路由定义
@router.get("/operators", response_model=Dict[str, OperatorInfo])
async def get_operators():
    """获取所有可用的操作类型"""
    return AnalyticsService.get_available_operators()


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建分析任务"""
    try:
        # 创建流水线
        pipeline = Pipeline(name=task.pipeline.name, description=task.pipeline.description)
        
        # 添加步骤
        for step in task.pipeline.steps:
            pipeline.add_step(step.operator_type, step.params)
        
        # 创建任务
        # 注意：这里使用了硬编码的用户ID，实际应用中应该从认证信息中获取
        user_id = "00000000-0000-0000-0000-000000000000"
        
        created_task = AnalyticsService.create_task(
            db=db,
            user_id=user_id,
            name=task.name,
            pipeline=pipeline,
            datasource_id=task.datasource_id
        )
        
        # 转换为响应格式
        response = TaskResponse(
            id=created_task.id,
            name=created_task.name,
            status=created_task.status,
            pipeline=PipelineResponse(
                id=pipeline.id,
                name=pipeline.name,
                description=pipeline.description,
                steps=[
                    PipelineStep(
                        id=step["id"],
                        operator_type=step["operator_type"],
                        params=step["params"]
                    )
                    for step in pipeline.steps
                ],
                created_at=pipeline.created_at.isoformat(),
                updated_at=pipeline.updated_at.isoformat()
            ),
            datasource_id=created_task.datasource_id,
            result_path=created_task.result_path,
            created_at=created_task.created_at.isoformat(),
            updated_at=created_task.updated_at.isoformat()
        )
        
        # 异步执行任务
        execute_analysis_task.delay(created_task.id)
        
        return response
    
    except AnalyticsException as e:
        logger.error(f"创建分析任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建分析任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分析任务失败: {str(e)}"
        )


@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(db: Session = Depends(get_db)):
    """获取所有分析任务"""
    try:
        # 注意：这里使用了硬编码的用户ID，实际应用中应该从认证信息中获取
        user_id = "00000000-0000-0000-0000-000000000000"
        
        tasks = AnalyticsService.get_user_tasks(db, user_id)
        
        # 转换为响应格式
        return [
            TaskResponse(
                id=task.id,
                name=task.name,
                status=task.status,
                pipeline=PipelineResponse(
                    id=task.pipeline.get("id", ""),
                    name=task.pipeline.get("name", ""),
                    description=task.pipeline.get("description", ""),
                    steps=[
                        PipelineStep(
                            id=step.get("id", ""),
                            operator_type=step["operator_type"],
                            params=step["params"]
                        )
                        for step in task.pipeline.get("steps", [])
                    ],
                    created_at=task.pipeline.get("created_at", ""),
                    updated_at=task.pipeline.get("updated_at", "")
                ),
                datasource_id=task.datasource_id,
                result_path=task.result_path,
                created_at=task.created_at.isoformat(),
                updated_at=task.updated_at.isoformat()
            )
            for task in tasks
        ]
    
    except Exception as e:
        logger.error(f"获取分析任务列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析任务列表失败: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """获取分析任务详情"""
    try:
        task = AnalyticsService.get_task(db, task_id)
        
        # 转换为响应格式
        return TaskResponse(
            id=task.id,
            name=task.name,
            status=task.status,
            pipeline=PipelineResponse(
                id=task.pipeline.get("id", ""),
                name=task.pipeline.get("name", ""),
                description=task.pipeline.get("description", ""),
                steps=[
                    PipelineStep(
                        id=step.get("id", ""),
                        operator_type=step["operator_type"],
                        params=step["params"]
                    )
                    for step in task.pipeline.get("steps", [])
                ],
                created_at=task.pipeline.get("created_at", ""),
                updated_at=task.pipeline.get("updated_at", "")
            ),
            datasource_id=task.datasource_id,
            result_path=task.result_path,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat()
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取分析任务详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析任务详情失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """获取分析任务状态"""
    try:
        task = AnalyticsService.get_task(db, task_id)
        
        return TaskStatusResponse(
            id=task.id,
            status=task.status,
            message=None
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取分析任务状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析任务状态失败: {str(e)}"
        )


@router.get("/tasks/{task_id}/logs", response_model=TaskLogResponse)
async def get_task_logs(
    task_id: str = Path(..., description="任务ID"),
    max_lines: int = Query(100, description="最大行数"),
    db: Session = Depends(get_db)
):
    """获取分析任务日志"""
    try:
        # 检查任务是否存在
        task = AnalyticsService.get_task(db, task_id)
        
        # 获取任务日志
        task_logger = get_task_logger(task_id)
        logs = task_logger.get_logs(max_lines)
        
        return TaskLogResponse(
            id=task.id,
            logs=logs
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取分析任务日志失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析任务日志失败: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """删除分析任务"""
    try:
        AnalyticsService.delete_task(db, task_id)
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除分析任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分析任务失败: {str(e)}"
        )


@router.post("/tasks/{task_id}/cancel", response_model=TaskStatusResponse)
async def cancel_task(
    task_id: str = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    """取消分析任务"""
    try:
        # 获取任务
        task = AnalyticsService.get_task(db, task_id)
        
        # 如果任务已经完成或失败，无法取消
        if task.status in ["completed", "failed", "canceled"]:
            return TaskStatusResponse(
                id=task.id,
                status=task.status,
                message=f"无法取消已{task.status}的任务"
            )
        
        # 更新任务状态
        AnalyticsService.update_task(db, task_id, status="canceled")
        
        # 异步取消任务
        from backend.src.core.tasks import cancel_analysis_task
        cancel_analysis_task.delay(task_id)
        
        return TaskStatusResponse(
            id=task.id,
            status="canceled",
            message="任务已取消"
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"取消分析任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消分析任务失败: {str(e)}"
        ) 