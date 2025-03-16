from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from backend.src.config.database import Base


class Dashboard(Base):
    """仪表盘模型"""
    
    __tablename__ = "dashboards"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, comment="仪表盘标题")
    description = Column(Text, nullable=True, comment="仪表盘描述")
    layout = Column(Text, nullable=True, comment="仪表盘布局(JSON)")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 暂时禁用关系
    # dashboard_items = relationship("DashboardItem", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dashboard(id={self.id}, title={self.title})>"


class DashboardItem(Base):
    """仪表盘项目模型"""
    
    __tablename__ = "dashboard_items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dashboard_id = Column(String(36), nullable=False)  # 暂时禁用外键约束
    chart_id = Column(String(36), nullable=False)  # 暂时禁用外键约束
    
    # 位置和大小
    position_x = Column(String(10), nullable=False, comment="X坐标")
    position_y = Column(String(10), nullable=False, comment="Y坐标")
    width = Column(String(10), nullable=False, comment="宽度")
    height = Column(String(10), nullable=False, comment="高度")
    
    # 配置
    config = Column(Text, nullable=True, comment="项目配置(JSON)")
    
    # 时间戳
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 暂时禁用关系
    # dashboard = relationship("Dashboard", back_populates="dashboard_items")
    
    def __repr__(self):
        return f"<DashboardItem(id={self.id}, dashboard_id={self.dashboard_id}, chart_id={self.chart_id})>" 