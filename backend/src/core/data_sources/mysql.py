import pandas as pd
from sqlalchemy import create_engine, inspect, text
from typing import Dict, Any, List, Optional
import pymysql
from .base import DataSource, DataSourceFactory
from src.utils.exceptions import DataSourceException
from src.utils.logger import setup_logger
import urllib.parse

# 创建日志记录器
logger = setup_logger("mysql_datasource")


class MySQLDataSource(DataSource):
    """MySQL数据源实现"""
    
    def __init__(self):
        """初始化MySQL数据源"""
        self.engine = None
        self.inspector = None
        self.connection_config = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到MySQL数据库
        
        Args:
            config: 连接配置，包含host, port, user, password, database等
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 处理密码中的特殊字符
            password = urllib.parse.quote_plus(config['password'])
            
            # 构建连接URL
            connection_url = f"mysql+pymysql://{config['user']}:{password}@{config['host']}:{config['port']}/{config['database']}"
            
            # 创建引擎
            self.engine = create_engine(
                connection_url,
                pool_size=5,
                max_overflow=10,
                pool_recycle=3600,
                pool_pre_ping=True
            )
            
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # 创建检查器
            self.inspector = inspect(self.engine)
            
            # 保存连接配置
            self.connection_config = config
            
            logger.info(f"成功连接到MySQL数据库: {config['host']}:{config['port']}/{config['database']}")
            return True
        
        except Exception as e:
            logger.error(f"连接MySQL数据库失败: {str(e)}")
            raise DataSourceException(f"连接MySQL数据库失败: {str(e)}")
    
    def disconnect(self) -> None:
        """断开与MySQL数据库的连接"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.inspector = None
            logger.info("已断开MySQL数据库连接")
    
    def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试MySQL数据库连接
        
        Args:
            config: 连接配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 创建临时连接
            connection = pymysql.connect(
                host=config['host'],
                port=int(config['port']),
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            
            # 测试连接
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # 关闭连接
            connection.close()
            
            logger.info(f"MySQL连接测试成功: {config['host']}:{config['port']}/{config['database']}")
            return True
        
        except Exception as e:
            logger.error(f"MySQL连接测试失败: {str(e)}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        获取数据库中的所有表名
        
        Returns:
            List[str]: 表名列表
        """
        if not self.engine or not self.inspector:
            raise DataSourceException("未连接到MySQL数据库")
        
        try:
            tables = self.inspector.get_table_names()
            logger.debug(f"获取到{len(tables)}个表")
            return tables
        
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise DataSourceException(f"获取表列表失败: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取指定表的结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict[str, Any]]: 表结构信息，包含字段名、类型等
        """
        if not self.engine or not self.inspector:
            raise DataSourceException("未连接到MySQL数据库")
        
        try:
            # 获取列信息
            columns = self.inspector.get_columns(table_name)
            
            # 格式化列信息
            schema = []
            for column in columns:
                schema.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column.get("nullable", True),
                    "default": column.get("default"),
                    "primary_key": column.get("primary_key", False)
                })
            
            logger.debug(f"获取表{table_name}的结构信息，共{len(schema)}列")
            return schema
        
        except Exception as e:
            logger.error(f"获取表{table_name}的结构信息失败: {str(e)}")
            raise DataSourceException(f"获取表{table_name}的结构信息失败: {str(e)}")
    
    def fetch_data(self, query: Dict[str, Any]) -> pd.DataFrame:
        """
        从MySQL数据库获取数据
        
        Args:
            query: 查询参数，包含sql或table_name和filters等
            
        Returns:
            pd.DataFrame: 查询结果数据
        """
        if not self.engine:
            raise DataSourceException("未连接到MySQL数据库")
        
        try:
            # 如果提供了SQL语句，直接执行
            if "sql" in query:
                sql = query["sql"]
                logger.debug(f"执行SQL查询: {sql}")
                return pd.read_sql(sql, self.engine)
            
            # 如果提供了表名和过滤条件，构建SQL语句
            elif "table_name" in query:
                table_name = query["table_name"]
                
                # 构建SELECT子句
                if "columns" in query and query["columns"]:
                    columns = ", ".join(query["columns"])
                else:
                    columns = "*"
                
                # 构建WHERE子句
                where_clause = ""
                if "filters" in query and query["filters"]:
                    conditions = []
                    for filter_item in query["filters"]:
                        if len(filter_item) == 3:
                            field, operator, value = filter_item
                            
                            # 处理不同类型的值
                            if isinstance(value, str):
                                value = f"'{value}'"
                            elif value is None:
                                value = "NULL"
                            else:
                                value = str(value)
                            
                            conditions.append(f"{field} {operator} {value}")
                    
                    if conditions:
                        where_clause = "WHERE " + " AND ".join(conditions)
                
                # 构建ORDER BY子句
                order_clause = ""
                if "order_by" in query and query["order_by"]:
                    order_items = []
                    for order_item in query["order_by"]:
                        if isinstance(order_item, tuple) and len(order_item) == 2:
                            field, direction = order_item
                            order_items.append(f"{field} {direction}")
                        else:
                            order_items.append(f"{order_item}")
                    
                    if order_items:
                        order_clause = "ORDER BY " + ", ".join(order_items)
                
                # 构建LIMIT子句
                limit_clause = ""
                if "limit" in query:
                    limit_clause = f"LIMIT {query['limit']}"
                    
                    if "offset" in query:
                        limit_clause += f" OFFSET {query['offset']}"
                
                # 组合SQL语句
                sql = f"SELECT {columns} FROM {table_name} {where_clause} {order_clause} {limit_clause}"
                sql = " ".join(sql.split())  # 移除多余空格
                
                logger.debug(f"执行SQL查询: {sql}")
                return pd.read_sql(sql, self.engine)
            
            else:
                raise DataSourceException("查询参数必须包含sql或table_name")
        
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise DataSourceException(f"执行查询失败: {str(e)}")
    
    def get_sample_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        获取表的样本数据
        
        Args:
            table_name: 表名
            limit: 返回的最大行数
            
        Returns:
            pd.DataFrame: 样本数据
        """
        query = {
            "table_name": table_name,
            "limit": limit
        }
        
        return self.fetch_data(query)


# 注册MySQL数据源
DataSourceFactory.register("mysql", MySQLDataSource) 