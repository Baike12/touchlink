#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建TouchLink应用所需的所有数据库和表
使用方法: python init_database.py
"""

import os
import sys
import argparse
import sqlalchemy as sa
from dotenv import load_dotenv
import urllib.parse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("init_database")

# 加载环境变量
load_dotenv()

# 数据库设置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "touchlink")
USER_DB_NAME = os.getenv("USER_DB_NAME", "user_database")

def get_admin_engine():
    """获取管理员数据库连接引擎"""
    password = urllib.parse.quote_plus(DB_PASSWORD)
    return sa.create_engine(
        f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/mysql"
    )

def get_db_engine(db_name):
    """获取指定数据库的连接引擎"""
    password = urllib.parse.quote_plus(DB_PASSWORD)
    return sa.create_engine(
        f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{db_name}"
    )

def create_database(db_name):
    """创建数据库"""
    try:
        engine = get_admin_engine()
        with engine.connect() as conn:
            conn.execute(sa.text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        logger.info(f"数据库 {db_name} 创建成功")
        return True
    except Exception as e:
        logger.error(f"创建数据库 {db_name} 失败: {str(e)}")
        return False

def init_main_tables():
    """初始化主数据库表"""
    try:
        engine = get_db_engine(DB_NAME)
        with engine.connect() as conn:
            # 数据源表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS data_sources (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(20) NOT NULL,
                config JSON NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 分析任务表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS analysis_tasks (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                pipeline JSON NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                result_path VARCHAR(255),
                datasource_id VARCHAR(36),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 导出任务表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS export_tasks (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(20) NOT NULL,
                config JSON NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'pending',
                result_path VARCHAR(255),
                analysis_task_id VARCHAR(36),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 图表表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS charts (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                type VARCHAR(50) NOT NULL,
                config TEXT NOT NULL,
                data_source TEXT,
                user_id VARCHAR(36) NULL,
                analysis_task_id VARCHAR(36),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 仪表盘表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS dashboards (
                id VARCHAR(36) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                layout TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 仪表盘项目表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS dashboard_items (
                id VARCHAR(36) PRIMARY KEY,
                dashboard_id VARCHAR(36) NOT NULL,
                chart_id VARCHAR(36) NOT NULL,
                position_x VARCHAR(10) NOT NULL,
                position_y VARCHAR(10) NOT NULL,
                width VARCHAR(10) NOT NULL,
                height VARCHAR(10) NOT NULL,
                config TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 数据分析模板表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS analytics_templates (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL COMMENT '模板名称',
                description VARCHAR(255) COMMENT '模板描述',
                datasource_id VARCHAR(36) NOT NULL COMMENT '数据源ID',
                tables TEXT NOT NULL COMMENT '选择的表',
                columns TEXT NOT NULL COMMENT '选择的列',
                join_relationships TEXT COMMENT 'JOIN关系',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            )
            """))
            
            conn.commit()
        
        logger.info("主数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"创建主数据库表失败: {str(e)}")
        return False

def init_user_tables():
    """初始化用户数据库表"""
    try:
        engine = get_db_engine(USER_DB_NAME)
        with engine.connect() as conn:
            # 用户表信息表
            conn.execute(sa.text("""
            CREATE TABLE IF NOT EXISTS user_table_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """))
            
            # 表字段信息表
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
        
        logger.info("用户数据库表创建成功")
        return True
    except Exception as e:
        logger.error(f"创建用户数据库表失败: {str(e)}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='初始化TouchLink数据库')
    parser.add_argument('--force', action='store_true', help='强制重新创建所有表')
    args = parser.parse_args()
    
    logger.info("开始初始化数据库...")
    
    # 创建主数据库
    if not create_database(DB_NAME):
        logger.error("主数据库创建失败，退出")
        sys.exit(1)
    
    # 创建用户数据库
    if not create_database(USER_DB_NAME):
        logger.error("用户数据库创建失败，退出")
        sys.exit(1)
    
    # 初始化主数据库表
    if not init_main_tables():
        logger.error("主数据库表初始化失败，退出")
        sys.exit(1)
    
    # 初始化用户数据库表
    if not init_user_tables():
        logger.error("用户数据库表初始化失败，退出")
        sys.exit(1)
    
    logger.info("数据库初始化完成！")

if __name__ == "__main__":
    main() 