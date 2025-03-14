from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
import urllib.parse

from src.api.deps import get_db
from src.config.settings import settings
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("user_tables")

# 创建路由
router = APIRouter(prefix="/user-tables", tags=["用户表"])

# 创建数据模型
class ColumnSchema(BaseModel):
    name: str
    type: str

class TableSchema(BaseModel):
    tableName: str
    columns: List[ColumnSchema]

# 处理密码中的特殊字符
password = urllib.parse.quote_plus(settings.DB_PASSWORD)

# 创建用户数据库引擎
user_db_engine = sa.create_engine(
    f"mysql+pymysql://{settings.DB_USER}:{password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.USER_DB_NAME}"
)

# 创建表
@router.post("", status_code=status.HTTP_201_CREATED)
def create_table(table: TableSchema, db: Session = Depends(get_db)):
    """创建用户表"""
    try:
        # 检查表名是否已存在
        result = db.execute(sa.text(
            "SELECT table_name FROM user_database.user_table_info WHERE table_name = :table_name"
        ), {"table_name": table.tableName})
        
        if result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"表 '{table.tableName}' 已存在"
            )
        
        # 创建表
        columns_sql = []
        for column in table.columns:
            column_type = ""
            if column.type == "int":
                column_type = "INT"
            elif column.type == "varchar":
                column_type = "VARCHAR(255)"
            elif column.type == "timestamp":
                column_type = "TIMESTAMP"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的数据类型: {column.type}"
                )
            
            columns_sql.append(f"`{column.name}` {column_type}")
        
        # 添加自增ID字段
        create_table_sql = f"""
        CREATE TABLE user_database.`{table.tableName}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            {', '.join(columns_sql)},
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        # 执行创建表SQL
        with user_db_engine.connect() as conn:
            conn.execute(sa.text(create_table_sql))
            conn.commit()
        
        # 记录表信息
        db.execute(sa.text(
            "INSERT INTO user_database.user_table_info (table_name) VALUES (:table_name)"
        ), {"table_name": table.tableName})
        
        # 记录字段信息
        for column in table.columns:
            db.execute(sa.text(
                """
                INSERT INTO user_database.user_table_column 
                (table_name, column_name, column_type) 
                VALUES (:table_name, :column_name, :column_type)
                """
            ), {
                "table_name": table.tableName,
                "column_name": column.name,
                "column_type": column.type
            })
        
        db.commit()
        
        return {"message": f"表 '{table.tableName}' 创建成功"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建表失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建表失败: {str(e)}"
        )

# 添加数据
@router.post("/{table_name}/data", status_code=status.HTTP_201_CREATED)
def add_data(table_name: str, data: Dict[str, Any], db: Session = Depends(get_db)):
    """向表中添加数据"""
    try:
        # 检查表是否存在
        result = db.execute(sa.text(
            "SELECT table_name FROM user_database.user_table_info WHERE table_name = :table_name"
        ), {"table_name": table_name})
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"表 '{table_name}' 不存在"
            )
        
        # 获取表字段信息
        result = db.execute(sa.text(
            """
            SELECT column_name, column_type 
            FROM user_database.user_table_column 
            WHERE table_name = :table_name
            """
        ), {"table_name": table_name})
        
        columns = {row[0]: row[1] for row in result.fetchall()}
        
        # 验证数据
        for column_name, column_type in columns.items():
            if column_name not in data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"缺少字段: {column_name}"
                )
            
            # 类型转换
            if column_type == "int":
                try:
                    if data[column_name] == '':
                        data[column_name] = None
                    elif data[column_name] is not None:
                        data[column_name] = int(data[column_name])
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"字段 '{column_name}' 必须是整数"
                    )
            elif column_type == "timestamp":
                # 处理空时间戳
                if data[column_name] == '':
                    data[column_name] = None
        
        # 构建插入SQL
        column_names = list(columns.keys())
        placeholders = [f":{name}" for name in column_names]
        
        insert_sql = f"""
        INSERT INTO user_database.`{table_name}` 
        (`{'`, `'.join(column_names)}`) 
        VALUES ({', '.join(placeholders)})
        """
        
        # 执行插入SQL
        with user_db_engine.connect() as conn:
            result = conn.execute(sa.text(insert_sql), data)
            conn.commit()
            last_id = result.lastrowid
        
        # 获取插入的数据
        select_sql = f"""
        SELECT * FROM user_database.`{table_name}` WHERE id = :id
        """
        
        with user_db_engine.connect() as conn:
            result = conn.execute(sa.text(select_sql), {"id": last_id})
            row = result.fetchone()
            
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="数据添加成功，但无法获取添加的数据"
                )
            
            # 转换为字典
            data = {}
            for idx, column in enumerate(result.keys()):
                data[column] = row[idx]
        
        return data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加数据失败: {str(e)}"
        )

# 获取表数据
@router.get("/{table_name}/data")
def get_table_data(table_name: str, db: Session = Depends(get_db)):
    """获取表数据"""
    try:
        # 检查表是否存在
        result = db.execute(sa.text(
            "SELECT table_name FROM user_database.user_table_info WHERE table_name = :table_name"
        ), {"table_name": table_name})
        
        if not result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"表 '{table_name}' 不存在"
            )
        
        # 获取表数据
        select_sql = f"""
        SELECT * FROM user_database.`{table_name}`
        """
        
        with user_db_engine.connect() as conn:
            result = conn.execute(sa.text(select_sql))
            rows = result.fetchall()
            
            # 转换为字典列表
            data = []
            for row in rows:
                item = {}
                for idx, column in enumerate(result.keys()):
                    item[column] = row[idx]
                data.append(item)
        
        return data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取表数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表数据失败: {str(e)}"
        )

# 获取所有表
@router.get("")
def get_tables(db: Session = Depends(get_db)):
    """获取所有用户表"""
    try:
        # 获取所有表
        result = db.execute(sa.text(
            """
            SELECT t.table_name, t.created_at, t.updated_at
            FROM user_database.user_table_info t
            ORDER BY t.created_at DESC
            """
        ))
        
        tables = []
        for row in result.fetchall():
            table_name = row[0]
            
            # 获取表字段
            column_result = db.execute(sa.text(
                """
                SELECT column_name, column_type
                FROM user_database.user_table_column
                WHERE table_name = :table_name
                """
            ), {"table_name": table_name})
            
            columns = []
            for column_row in column_result.fetchall():
                columns.append({
                    "name": column_row[0],
                    "type": column_row[1]
                })
            
            tables.append({
                "tableName": table_name,
                "columns": columns,
                "createdAt": row[1].isoformat() if row[1] else None,
                "updatedAt": row[2].isoformat() if row[2] else None
            })
        
        return tables
    
    except Exception as e:
        logger.error(f"获取表列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表列表失败: {str(e)}"
        ) 