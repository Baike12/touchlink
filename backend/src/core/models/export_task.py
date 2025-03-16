from sqlalchemy import Column, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from backend.src.config.database import Base


class ExportTask(Base):
    """导出任务模型"""
    __tablename__ = "export_tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)  # 暂时禁用外键约束
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # excel, csv
    config = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    result_path = Column(String(255), nullable=True)
    analysis_task_id = Column(String(36), nullable=True)  # 暂时禁用外键约束
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 暂时禁用关系
    # user = relationship("User", back_populates="export_tasks")
    # analysis_task = relationship("AnalysisTask")
    
    def __repr__(self):
        return f"<ExportTask(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"
