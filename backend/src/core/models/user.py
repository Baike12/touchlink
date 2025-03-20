from sqlalchemy import Column, String, DateTime, func, Boolean
from sqlalchemy.orm import relationship
import uuid
from src.config.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 暂时禁用关系
    # data_sources = relationship("DataSource", back_populates="user", cascade="all, delete-orphan")
    # analysis_tasks = relationship("AnalysisTask", back_populates="user", cascade="all, delete-orphan")
    # export_tasks = relationship("ExportTask", back_populates="user", cascade="all, delete-orphan")
    # charts = relationship("Chart", back_populates="user", cascade="all, delete-orphan")
    # dashboards = relationship("Dashboard", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>" 