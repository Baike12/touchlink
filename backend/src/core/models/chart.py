from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from src.config.database import Base


class Chart(Base):
    """图表模型"""
    __tablename__ = "charts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, comment='图表标题')
    description = Column(Text, nullable=True, comment='图表描述')
    type = Column(String(50), nullable=False, comment='图表类型')
    config = Column(Text, nullable=False, comment='图表配置(JSON)')
    data_source = Column(Text, nullable=True, comment='数据源配置(JSON)')
    user_id = Column(String(36), nullable=True)  # 设置为可为空
    analysis_task_id = Column(String(36), nullable=True)  # 暂时禁用外键约束
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 暂时禁用关系
    # user = relationship("User", back_populates="charts")
    # analysis_task = relationship("AnalysisTask", back_populates="charts")
    
    def __repr__(self):
        return f"<Chart(id={self.id}, title={self.title}, type={self.type})>" 