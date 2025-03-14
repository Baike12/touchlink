from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .chart import ChartResponse


class DashboardBase(BaseModel):
    """仪表盘基础模式"""
    title: str = Field(..., description="仪表盘标题")
    description: Optional[str] = Field(None, description="仪表盘描述")
    layout: Optional[Dict[str, Any]] = Field(None, description="仪表盘布局")


class DashboardCreate(DashboardBase):
    """创建仪表盘模式"""
    pass


class DashboardUpdate(BaseModel):
    """更新仪表盘模式"""
    title: Optional[str] = Field(None, description="仪表盘标题")
    description: Optional[str] = Field(None, description="仪表盘描述")
    layout: Optional[Dict[str, Any]] = Field(None, description="仪表盘布局")


class DashboardResponse(DashboardBase):
    """仪表盘响应模式"""
    id: str = Field(..., description="仪表盘ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True


class DashboardItemBase(BaseModel):
    """仪表盘项目基础模式"""
    position_x: int = Field(0, description="X坐标")
    position_y: int = Field(0, description="Y坐标")
    width: int = Field(4, description="宽度")
    height: int = Field(4, description="高度")
    config: Optional[Dict[str, Any]] = Field(None, description="项目配置")


class DashboardItemCreate(DashboardItemBase):
    """创建仪表盘项目模式"""
    chart_id: str = Field(..., description="图表ID")


class DashboardItemUpdate(BaseModel):
    """更新仪表盘项目模式"""
    position_x: Optional[int] = Field(None, description="X坐标")
    position_y: Optional[int] = Field(None, description="Y坐标")
    width: Optional[int] = Field(None, description="宽度")
    height: Optional[int] = Field(None, description="高度")
    config: Optional[Dict[str, Any]] = Field(None, description="项目配置")


class DashboardItemResponse(DashboardItemBase):
    """仪表盘项目响应模式"""
    id: str = Field(..., description="项目ID")
    chart_id: str = Field(..., description="图表ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True


class ChartInfo(BaseModel):
    """图表信息模式"""
    id: str = Field(..., description="图表ID")
    title: str = Field(..., description="图表标题")
    type: str = Field(..., description="图表类型")
    config: Dict[str, Any] = Field(..., description="图表配置")


class DashboardItemWithChart(DashboardItemBase):
    """带图表的仪表盘项目模式"""
    id: str = Field(..., description="项目ID")
    chart: ChartInfo = Field(..., description="图表信息")


class DashboardWithItems(DashboardResponse):
    """带项目的仪表盘模式"""
    items: List[DashboardItemWithChart] = Field([], description="仪表盘项目") 