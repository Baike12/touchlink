from sqlalchemy.orm import Session
import uuid
import os
import sqlalchemy as sa
import urllib.parse

from src.core.models import Base, User
from src.config.database import engine, get_db
from src.config.settings import settings
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("init_db")


def init_db():
    """初始化数据库"""
    logger.info("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")
    
    # 初始化用户数据库
    init_user_database()
    
    # 暂时禁用创建默认用户
    # create_default_user()


def init_user_database():
    """初始化用户数据库"""
    try:
        # 处理密码中的特殊字符
        password = urllib.parse.quote_plus(settings.DB_PASSWORD)
        
        # 创建数据库连接
        admin_engine = sa.create_engine(
            f"mysql+pymysql://{settings.DB_USER}:{password}@{settings.DB_HOST}:{settings.DB_PORT}/mysql"
        )
        
        # 创建用户数据库
        with admin_engine.connect() as conn:
            conn.execute(sa.text(f"CREATE DATABASE IF NOT EXISTS {settings.USER_DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        logger.info(f"用户数据库 {settings.USER_DB_NAME} 创建完成")
        
        # 创建用户数据库连接
        user_db_engine = sa.create_engine(
            f"mysql+pymysql://{settings.DB_USER}:{password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.USER_DB_NAME}"
        )
        
        # 创建用户表信息表
        with user_db_engine.connect() as conn:
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS user_table_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 创建表字段信息表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS user_table_column (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(255) NOT NULL,
                column_name VARCHAR(255) NOT NULL,
                column_type VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (table_name) REFERENCES user_table_info(table_name) ON DELETE CASCADE,
                UNIQUE KEY (table_name, column_name)
            )
            """))
            
            conn.commit()
        
        logger.info("用户数据库表创建完成")
    
    except Exception as e:
        logger.error(f"初始化用户数据库失败: {str(e)}")


def create_default_user():
    """创建默认用户"""
    db = next(get_db())
    
    # 检查是否已存在默认用户
    default_user = db.query(User).filter(User.username == "admin").first()
    if default_user:
        logger.info("默认用户已存在")
        return
    
    # 创建默认用户
    default_user = User(
        id="00000000-0000-0000-0000-000000000000",
        username="admin",
        password="admin",  # 实际应用中应该使用加密密码
        email="admin@example.com"
    )
    
    db.add(default_user)
    db.commit()
    
    logger.info(f"创建默认用户: {default_user.username}")


if __name__ == "__main__":
    init_db() 