from sqlalchemy import Column, String, JSON, DateTime, func
import uuid
from src.config.database import Base


class DataSource(Base):
    """数据源模型"""
    __tablename__ = "data_sources"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), default="00000000-0000-0000-0000-000000000000")
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name}, type={self.type})>" 