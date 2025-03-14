from sqlalchemy import Column, String, Text, DateTime, func
import uuid
import json
from src.config.database import Base


class AnalyticsTemplate(Base):
    """数据分析模板模型"""
    __tablename__ = "analytics_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, default="00000000-0000-0000-0000-000000000000", comment="用户ID")
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(String(255), nullable=True, comment="模板描述")
    datasource_id = Column(String(36), nullable=False, comment="数据源ID")
    tables = Column(Text, nullable=False, comment="选择的表")
    columns = Column(Text, nullable=False, comment="选择的列")
    join_relationships = Column(Text, nullable=True, comment="JOIN关系")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AnalyticsTemplate(id={self.id}, name={self.name})>" 