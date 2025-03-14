from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ChartBase(BaseModel):
    """图表基础模式"""
    title: str = Field(..., description="图表标题")
    description: Optional[str] = Field(None, description="图表描述")
    type: str = Field(..., description="图表类型")
    config: Dict[str, Any] = Field(..., description="图表配置")
    data_source: Optional[Dict[str, Any]] = Field(None, description="数据源配置")


class ChartCreate(ChartBase):
    """创建图表模式"""
    analysis_task_id: Optional[str] = Field(None, description="分析任务ID")


class ChartUpdate(BaseModel):
    """更新图表模式"""
    title: Optional[str] = Field(None, description="图表标题")
    description: Optional[str] = Field(None, description="图表描述")
    type: Optional[str] = Field(None, description="图表类型")
    config: Optional[Dict[str, Any]] = Field(None, description="图表配置")
    data_source: Optional[Dict[str, Any]] = Field(None, description="数据源配置")


class ChartResponse(ChartBase):
    """图表响应模式"""
    id: str = Field(..., description="图表ID")
    analysis_task_id: Optional[str] = Field(None, description="分析任务ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True


class ChartTypeResponse(BaseModel):
    """图表类型响应模式"""
    type: str = Field(..., description="图表类型")
    name: str = Field(..., description="图表名称")


class ChartOptionsResponse(BaseModel):
    """图表选项响应模式"""
    options: Dict[str, Any] = Field(..., description="图表选项") 