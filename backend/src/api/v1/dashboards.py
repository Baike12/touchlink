from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.services import DashboardService
from src.api.deps import get_db, get_current_user
from src.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)
from src.schemas.user import User
from src.schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    DashboardWithItems,
    DashboardItemCreate,
    DashboardItemUpdate,
    DashboardItemResponse
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])


@router.post("", response_model=DashboardResponse)
def create_dashboard(
    dashboard_data: DashboardCreate,
    db: Session = Depends(get_db)
):
    """
    创建仪表盘
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard = dashboard_service.create_dashboard(
            title=dashboard_data.title,
            description=dashboard_data.description,
            layout=dashboard_data.layout
        )
        
        return dashboard
    
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建仪表盘时发生错误: {str(e)}"
        )


@router.get("", response_model=List[DashboardResponse])
def get_dashboards(
    db: Session = Depends(get_db)
):
    """
    获取仪表盘列表
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboards = dashboard_service.get_dashboards()
        
        return dashboards
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表盘列表时发生错误: {str(e)}"
        )


@router.get("/{dashboard_id}", response_model=DashboardResponse)
def get_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """
    获取仪表盘
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard = dashboard_service.get_dashboard(
            dashboard_id=dashboard_id
        )
        
        return dashboard
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表盘时发生错误: {str(e)}"
        )


@router.get("/{dashboard_id}/items", response_model=DashboardWithItems)
def get_dashboard_with_items(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """
    获取仪表盘及其项目
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard_with_items = dashboard_service.get_dashboard_with_items(
            dashboard_id=dashboard_id
        )
        
        return dashboard_with_items
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表盘及其项目时发生错误: {str(e)}"
        )


@router.put("/{dashboard_id}", response_model=DashboardResponse)
def update_dashboard(
    dashboard_id: str,
    dashboard_data: DashboardUpdate,
    db: Session = Depends(get_db)
):
    """
    更新仪表盘
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard = dashboard_service.update_dashboard(
            dashboard_id=dashboard_id,
            title=dashboard_data.title,
            description=dashboard_data.description,
            layout=dashboard_data.layout
        )
        
        return dashboard
    
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
            detail=f"更新仪表盘时发生错误: {str(e)}"
        )


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """
    删除仪表盘
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard_service.delete_dashboard(
            dashboard_id=dashboard_id
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
            detail=f"删除仪表盘时发生错误: {str(e)}"
        )


@router.post("/{dashboard_id}/items", response_model=DashboardItemResponse)
def add_chart_to_dashboard(
    dashboard_id: str,
    item_data: DashboardItemCreate,
    db: Session = Depends(get_db)
):
    """
    添加图表到仪表盘
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard_item = dashboard_service.add_chart_to_dashboard(
            dashboard_id=dashboard_id,
            chart_id=item_data.chart_id,
            position_x=item_data.position_x,
            position_y=item_data.position_y,
            width=item_data.width,
            height=item_data.height,
            config=item_data.config
        )
        
        return dashboard_item
    
    except ResourceNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
            detail=f"添加图表到仪表盘时发生错误: {str(e)}"
        )


@router.put("/items/{item_id}", response_model=DashboardItemResponse)
def update_dashboard_item(
    item_id: str,
    item_data: DashboardItemUpdate,
    db: Session = Depends(get_db)
):
    """
    更新仪表盘项目
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard_item = dashboard_service.update_dashboard_item(
            item_id=item_id,
            position_x=item_data.position_x,
            position_y=item_data.position_y,
            width=item_data.width,
            height=item_data.height,
            config=item_data.config
        )
        
        return dashboard_item
    
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
            detail=f"更新仪表盘项目时发生错误: {str(e)}"
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_chart_from_dashboard(
    item_id: str,
    db: Session = Depends(get_db)
):
    """
    从仪表盘中移除图表
    """
    try:
        dashboard_service = DashboardService(db)
        
        dashboard_service.remove_chart_from_dashboard(
            item_id=item_id
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
            detail=f"从仪表盘中移除图表时发生错误: {str(e)}"
        ) 