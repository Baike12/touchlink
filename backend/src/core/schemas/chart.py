from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ChartBase(BaseModel):
    """图表基础模型"""
    title: str
    description: Optional[str] = None
    type: str
    config: Dict[str, Any]
    data_source: Optional[Dict[str, Any]] = None
    analysis_task_id: Optional[str] = None


class ChartCreate(ChartBase):
    """创建图表请求模型"""
    tables: Optional[List[str]] = None


class ChartUpdate(BaseModel):
    """更新图表请求模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    data_source: Optional[Dict[str, Any]] = None


class ChartResponse(ChartBase):
    """图表响应模型"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ChartList(BaseModel):
    """图表列表项模型"""
    id: str
    title: str
    description: Optional[str] = None
    type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ChartTypeResponse(BaseModel):
    """图表类型响应模型"""
    type: str
    name: str


class ChartOptionsResponse(BaseModel):
    """图表选项响应模型"""
    options: Dict[str, Any] 