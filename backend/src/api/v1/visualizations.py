from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from sqlalchemy.orm import Session
import pandas as pd
import json
import uuid

from backend.src.core.services import VisualizationService
from backend.src.core.visualization.chart_service import CHART_TYPES
from backend.src.api.deps import get_db
from backend.src.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)
from backend.src.schemas.chart import (
    ChartCreate,
    ChartUpdate,
    ChartResponse,
    ChartTypeResponse,
    ChartOptionsResponse
)

router = APIRouter(prefix="/visualizations", tags=["visualizations"])


@router.post("/charts", response_model=ChartResponse)
def create_chart(
    chart_data: ChartCreate,
    db: Session = Depends(get_db)
):
    """
    创建图表
    """
    try:
        visualization_service = VisualizationService(db)
        
        chart = visualization_service.create_chart(
            user_id=current_user.id,
            title=chart_data.title,
            description=chart_data.description,
            chart_type=chart_data.type,
            config=chart_data.config,
            analysis_task_id=chart_data.analysis_task_id,
            data_source=chart_data.data_source
        )
        
        return ChartResponse(
            id=chart.id,
            title=chart.title,
            description=chart.description,
            type=chart.type,
            config=json.loads(chart.config),
            data_source=json.loads(chart.data_source) if chart.data_source else None,
            analysis_task_id=chart.analysis_task_id,
            created_at=chart.created_at,
            updated_at=chart.updated_at
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建图表时发生错误: {str(e)}"
        )


@router.get("/charts", response_model=List[ChartResponse])
def get_charts(
    analysis_task_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取图表列表
    """
    try:
        visualization_service = VisualizationService(db)
        
        charts = visualization_service.get_charts(
            user_id=current_user.id,
            analysis_task_id=analysis_task_id
        )
        
        return [
            ChartResponse(
                id=chart.id,
                title=chart.title,
                description=chart.description,
                type=chart.type,
                config=json.loads(chart.config),
                data_source=json.loads(chart.data_source) if chart.data_source else None,
                analysis_task_id=chart.analysis_task_id,
                created_at=chart.created_at,
                updated_at=chart.updated_at
            )
            for chart in charts
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表列表时发生错误: {str(e)}"
        )


@router.get("/charts/{chart_id}", response_model=ChartResponse)
def get_chart(
    chart_id: str,
    db: Session = Depends(get_db)
):
    """
    获取图表
    """
    try:
        visualization_service = VisualizationService(db)
        
        chart = visualization_service.get_chart(
            chart_id=chart_id,
            user_id=current_user.id
        )
        
        return ChartResponse(
            id=chart.id,
            title=chart.title,
            description=chart.description,
            type=chart.type,
            config=json.loads(chart.config),
            data_source=json.loads(chart.data_source) if chart.data_source else None,
            analysis_task_id=chart.analysis_task_id,
            created_at=chart.created_at,
            updated_at=chart.updated_at
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表时发生错误: {str(e)}"
        )


@router.put("/charts/{chart_id}", response_model=ChartResponse)
def update_chart(
    chart_id: str,
    chart_data: ChartUpdate,
    db: Session = Depends(get_db)
):
    """
    更新图表
    """
    try:
        visualization_service = VisualizationService(db)
        
        chart = visualization_service.update_chart(
            chart_id=chart_id,
            user_id=current_user.id,
            title=chart_data.title,
            description=chart_data.description,
            chart_type=chart_data.type,
            config=chart_data.config,
            data_source=chart_data.data_source
        )
        
        return ChartResponse(
            id=chart.id,
            title=chart.title,
            description=chart.description,
            type=chart.type,
            config=json.loads(chart.config),
            data_source=json.loads(chart.data_source) if chart.data_source else None,
            analysis_task_id=chart.analysis_task_id,
            created_at=chart.created_at,
            updated_at=chart.updated_at
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新图表时发生错误: {str(e)}"
        )


@router.delete("/charts/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chart(
    chart_id: str,
    db: Session = Depends(get_db)
):
    """
    删除图表
    """
    try:
        visualization_service = VisualizationService(db)
        
        visualization_service.delete_chart(
            chart_id=chart_id,
            user_id=current_user.id
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除图表时发生错误: {str(e)}"
        )


@router.get("/charts/{chart_id}/options", response_model=ChartOptionsResponse)
def get_chart_options(
    chart_id: str,
    db: Session = Depends(get_db)
):
    """
    获取图表选项
    """
    try:
        visualization_service = VisualizationService(db)
        
        options = visualization_service.generate_chart_options(
            chart_id=chart_id,
            user_id=current_user.id
        )
        
        return ChartOptionsResponse(options=options)
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图表选项时发生错误: {str(e)}"
        )


@router.post("/charts/{chart_id}/data", response_model=ChartOptionsResponse)
async def generate_chart_with_data(
    chart_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    使用上传的数据生成图表
    """
    try:
        # 读取上传的文件
        content = await file.read()
        
        # 根据文件类型解析数据
        if file.filename.endswith('.csv'):
            import io
            data = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith('.xlsx'):
            import io
            data = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.json'):
            data = pd.DataFrame(json.loads(content.decode('utf-8')))
        else:
            raise ValidationException("不支持的文件类型，请上传CSV、Excel或JSON文件")
        
        # 生成图表选项
        visualization_service = VisualizationService(db)
        
        options = visualization_service.generate_chart_options(
            chart_id=chart_id,
            user_id=current_user.id,
            data=data
        )
        
        return ChartOptionsResponse(options=options)
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成图表时发生错误: {str(e)}"
        )


@router.get("/types", response_model=List[ChartTypeResponse])
def get_chart_types():
    """
    获取支持的图表类型
    """
    return [
        ChartTypeResponse(
            type=chart_type,
            name=chart_type.capitalize()
        )
        for chart_type in CHART_TYPES
    ] 