from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import json

from backend.src.api.deps import get_db, get_current_user
from backend.src.schemas.user import User
from backend.src.core.schemas.chart import (
    ChartCreate,
    ChartUpdate,
    ChartResponse,
    ChartTypeResponse,
    ChartOptionsResponse,
    ChartList
)
from backend.src.utils.logger import setup_logger
from backend.src.core.services.visualization_service import VisualizationService
from backend.src.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)

# 创建日志记录器
logger = setup_logger("charts_api")

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("", response_model=List[ChartList])
def get_charts(
    analysis_task_id: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取图表列表
    """
    from backend.src.core.services import VisualizationService
    
    try:
        visualization_service = VisualizationService(db)
        
        # 获取图表列表
        charts = visualization_service.get_charts()
        
        # 手动构建响应列表，避免ORM模式转换问题
        result = []
        for chart in charts:
            result.append({
                "id": chart.id,
                "title": chart.title,
                "description": chart.description,
                "type": chart.type,
                "config": json.loads(chart.config) if isinstance(chart.config, str) else chart.config,
                "data_source": json.loads(chart.data_source) if chart.data_source and isinstance(chart.data_source, str) else chart.data_source,
                "analysis_task_id": chart.analysis_task_id,
                "created_at": chart.created_at,
                "updated_at": chart.updated_at
            })
        
        return result
    
    except Exception as e:
        logger.error(f"获取图表列表时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表列表时发生错误: {str(e)}"
        )


@router.get("/types", response_model=List[ChartTypeResponse])
def get_chart_types():
    """
    获取图表类型列表
    """
    # 返回支持的图表类型
    return [
        {"type": "line", "name": "折线图"},
        {"type": "bar", "name": "柱状图"},
        {"type": "pie", "name": "饼图"},
        {"type": "scatter", "name": "散点图"},
        {"type": "area", "name": "面积图"},
        {"type": "radar", "name": "雷达图"},
        {"type": "heatmap", "name": "热力图"},
        {"type": "table", "name": "表格"}
    ]


@router.get("/options/{chart_type}", response_model=ChartOptionsResponse)
def get_chart_options(chart_type: str):
    """
    获取图表选项
    """
    # 根据图表类型返回对应的选项
    options = {
        "line": {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": []
        },
        "bar": {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": []
        },
        "pie": {
            "series": [{
                "type": "pie",
                "radius": "50%",
                "data": []
            }]
        },
        "scatter": {
            "xAxis": {"type": "value"},
            "yAxis": {"type": "value"},
            "series": []
        },
        "area": {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": []
        },
        "radar": {
            "radar": {
                "indicator": []
            },
            "series": []
        },
        "heatmap": {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "category"},
            "visualMap": {
                "min": 0,
                "max": 10,
                "calculable": true
            },
            "series": []
        },
        "table": {
            "columns": [],
            "data": []
        }
    }
    
    if chart_type not in options:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"不支持的图表类型: {chart_type}"
        )
    
    return {"options": options[chart_type]}


@router.post("", response_model=ChartResponse, status_code=status.HTTP_201_CREATED)
def create_chart(
    chart_data: ChartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建图表
    """
    try:
        # 记录请求数据
        logger.info(f"创建图表请求: 用户={current_user.username}, 标题={chart_data.title}, 类型={chart_data.type}")
        
        # 验证必要字段
        if not chart_data.title:
            logger.error("创建图表失败: 缺少标题")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少标题"
            )
        
        if not chart_data.type:
            logger.error("创建图表失败: 缺少图表类型")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少图表类型"
            )
        
        if not chart_data.config:
            logger.error("创建图表失败: 缺少图表配置")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少图表配置"
            )
        
        # 创建可视化服务
        try:
            visualization_service = VisualizationService(db)
        except Exception as e:
            logger.error(f"创建可视化服务失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建可视化服务失败: {str(e)}"
            )
        
        # 创建图表
        try:
            chart = visualization_service.create_chart(
                title=chart_data.title,
                chart_type=chart_data.type,
                config=chart_data.config,
                description=chart_data.description,
                analysis_task_id=chart_data.analysis_task_id,
                data_source=chart_data.data_source,
                tables=chart_data.tables
            )
            
            logger.info(f"图表创建成功: {chart.id}")
        except ValidationException as e:
            logger.error(f"图表验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except DatabaseException as e:
            logger.error(f"图表创建数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"图表创建未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建图表失败: {str(e)}"
            )
        
        # 构建响应
        try:
            return ChartResponse(
                id=chart.id,
                title=chart.title,
                description=chart.description,
                type=chart.type,
                config=chart_data.config,
                created_at=chart.created_at,
                updated_at=chart.updated_at
            )
        except Exception as e:
            # 注意：这里不回滚图表创建，因为图表已经创建成功
            logger.error(f"构建图表响应失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"构建图表响应失败: {str(e)}"
            )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    
    except Exception as e:
        # 处理其他异常
        logger.error(f"创建图表时发生未捕获的异常: {str(e)}")
        logger.exception("创建图表详细错误:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建图表时发生未知错误: {str(e)}"
        )


@router.get("/{chart_id}/data", response_model=Dict[str, Any])
def get_chart_data(
    chart_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取图表数据（从数据源加载实际数据）
    """
    try:
        # 记录请求
        logger.info(f"获取图表数据请求: 用户={current_user.username}, 图表ID={chart_id}")
        
        # 创建可视化服务
        try:
            visualization_service = VisualizationService(db)
        except Exception as e:
            logger.error(f"创建可视化服务失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建可视化服务失败: {str(e)}"
            )
        
        # 加载图表数据
        try:
            chart_data = visualization_service.load_chart_data(
                chart_id=chart_id
            )
            
            logger.info(f"图表数据加载成功: {chart_id}")
            return chart_data
        
        except ResourceNotFoundException as e:
            logger.error(f"图表不存在: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        
        except ValidationException as e:
            logger.error(f"图表数据验证失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        except DatabaseException as e:
            logger.error(f"图表数据加载数据库错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        except Exception as e:
            logger.error(f"图表数据加载未知错误: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"加载图表数据失败: {str(e)}"
            )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    
    except Exception as e:
        # 处理其他异常
        logger.error(f"获取图表数据时发生未捕获的异常: {str(e)}")
        logger.exception("获取图表数据详细错误:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表数据时发生未知错误: {str(e)}"
        )


@router.get("/{chart_id}", response_model=ChartResponse)
def get_chart(
    chart_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取图表
    """
    from backend.src.core.services import VisualizationService
    from backend.src.utils.exceptions import ResourceNotFoundException
    
    try:
        visualization_service = VisualizationService(db)
        
        # 获取图表
        chart = visualization_service.get_chart(chart_id)
        
        # 手动构建响应，避免ORM模式转换问题
        return {
            "id": chart.id,
            "title": chart.title,
            "description": chart.description,
            "type": chart.type,
            "config": json.loads(chart.config) if isinstance(chart.config, str) else chart.config,
            "data_source": json.loads(chart.data_source) if chart.data_source and isinstance(chart.data_source, str) else chart.data_source,
            "analysis_task_id": chart.analysis_task_id,
            "created_at": chart.created_at,
            "updated_at": chart.updated_at
        }
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        logger.error(f"获取图表时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表时发生错误: {str(e)}"
        )


@router.put("/{chart_id}", response_model=ChartResponse)
def update_chart(
    chart_id: str,
    chart_data: ChartUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新图表
    """
    # 临时实现，返回一个模拟的图表响应
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"图表不存在: {chart_id}"
    )


@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart(
    chart_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除图表
    """
    # 临时实现，返回一个成功响应
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"图表不存在: {chart_id}"
    )


@router.post("/preview", response_model=Dict[str, Any])
def preview_chart(
    chart_data: ChartCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    预览图表
    """
    # 临时实现，返回一个模拟的预览数据
    return {
        "data": {
            "categories": ["类别1", "类别2", "类别3", "类别4", "类别5"],
            "series": [
                {
                    "name": "系列1",
                    "data": [120, 200, 150, 80, 70]
                },
                {
                    "name": "系列2",
                    "data": [20, 100, 50, 180, 170]
                }
            ]
        }
    } 