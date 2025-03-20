from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import get_database_url

# 创建数据库引擎
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,  # 自动检测连接是否有效
    pool_recycle=3600,   # 一小时后回收连接
    echo=False           # 设置为True可以查看SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

# 获取数据库会话
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_database_url():
    """获取用户数据库URL，用于存储导入的Excel数据"""
    return get_database_url() 