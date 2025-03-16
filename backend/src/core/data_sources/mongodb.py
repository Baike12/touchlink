import pandas as pd
from typing import Dict, Any, List, Optional
import pymongo
from bson import ObjectId
from .base import DataSource, DataSourceFactory
from backend.src.utils.exceptions import DataSourceException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("mongodb_datasource")


class MongoDBDataSource(DataSource):
    """MongoDB数据源实现"""
    
    def __init__(self):
        """初始化MongoDB数据源"""
        self.client = None
        self.db = None
        self.connection_config = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到MongoDB数据库
        
        Args:
            config: 连接配置，包含host, port, user, password, database等
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 构建连接URL
            if config.get('user') and config.get('password'):
                connection_url = f"mongodb://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            else:
                connection_url = f"mongodb://{config['host']}:{config['port']}/{config['database']}"
            
            # 创建客户端
            self.client = pymongo.MongoClient(connection_url)
            
            # 测试连接
            self.client.admin.command('ping')
            
            # 选择数据库
            self.db = self.client[config['database']]
            
            # 保存连接配置
            self.connection_config = config
            
            logger.info(f"成功连接到MongoDB数据库: {config['host']}:{config['port']}/{config['database']}")
            return True
        
        except Exception as e:
            logger.error(f"连接MongoDB数据库失败: {str(e)}")
            raise DataSourceException(f"连接MongoDB数据库失败: {str(e)}")
    
    def disconnect(self) -> None:
        """断开与MongoDB数据库的连接"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("已断开MongoDB数据库连接")
    
    def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试MongoDB数据库连接
        
        Args:
            config: 连接配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 构建连接URL
            if config.get('user') and config.get('password'):
                connection_url = f"mongodb://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            else:
                connection_url = f"mongodb://{config['host']}:{config['port']}/{config['database']}"
            
            # 创建临时客户端
            client = pymongo.MongoClient(connection_url, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            client.admin.command('ping')
            
            # 关闭连接
            client.close()
            
            logger.info(f"MongoDB连接测试成功: {config['host']}:{config['port']}/{config['database']}")
            return True
        
        except Exception as e:
            logger.error(f"MongoDB连接测试失败: {str(e)}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        获取数据库中的所有集合名
        
        Returns:
            List[str]: 集合名列表
        """
        if not self.db:
            raise DataSourceException("未连接到MongoDB数据库")
        
        try:
            collections = self.db.list_collection_names()
            logger.debug(f"获取到{len(collections)}个集合")
            return collections
        
        except Exception as e:
            logger.error(f"获取集合列表失败: {str(e)}")
            raise DataSourceException(f"获取集合列表失败: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取指定集合的结构信息
        
        Args:
            table_name: 集合名
            
        Returns:
            List[Dict[str, Any]]: 集合结构信息，包含字段名、类型等
        """
        if not self.db:
            raise DataSourceException("未连接到MongoDB数据库")
        
        try:
            # 获取集合
            collection = self.db[table_name]
            
            # 获取一个文档样本
            sample = collection.find_one()
            if not sample:
                return []
            
            # 分析文档结构
            schema = []
            for field, value in sample.items():
                if field == '_id':
                    schema.append({
                        "name": field,
                        "type": "ObjectId",
                        "nullable": False,
                        "default": None,
                        "primary_key": True
                    })
                else:
                    schema.append({
                        "name": field,
                        "type": type(value).__name__,
                        "nullable": True,
                        "default": None,
                        "primary_key": False
                    })
            
            logger.debug(f"获取集合{table_name}的结构信息，共{len(schema)}个字段")
            return schema
        
        except Exception as e:
            logger.error(f"获取集合{table_name}的结构信息失败: {str(e)}")
            raise DataSourceException(f"获取集合{table_name}的结构信息失败: {str(e)}")
    
    def fetch_data(self, query: Dict[str, Any]) -> pd.DataFrame:
        """
        从MongoDB获取数据
        
        Args:
            query: 查询参数，包含collection, filter, projection, limit等
            
        Returns:
            pd.DataFrame: 查询结果数据
        """
        if not self.db:
            raise DataSourceException("未连接到MongoDB数据库")
        
        try:
            # 获取集合名
            collection_name = query.get('collection')
            if not collection_name:
                raise DataSourceException("查询参数必须包含collection")
            
            # 获取集合
            collection = self.db[collection_name]
            
            # 构建查询参数
            filter_dict = query.get('filter', {})
            projection = query.get('projection', None)
            limit = query.get('limit', 0)
            skip = query.get('skip', 0)
            sort = query.get('sort', None)
            
            # 执行查询
            cursor = collection.find(
                filter=filter_dict,
                projection=projection,
                skip=skip,
                limit=limit,
                sort=sort
            )
            
            # 转换为DataFrame
            data = list(cursor)
            
            # 处理ObjectId
            for doc in data:
                for key, value in doc.items():
                    if isinstance(value, ObjectId):
                        doc[key] = str(value)
            
            df = pd.DataFrame(data)
            
            logger.debug(f"从集合{collection_name}获取数据，共{len(df)}行")
            return df
        
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise DataSourceException(f"执行查询失败: {str(e)}")
    
    def get_sample_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        获取集合的样本数据
        
        Args:
            table_name: 集合名
            limit: 返回的最大行数
            
        Returns:
            pd.DataFrame: 样本数据
        """
        query = {
            'collection': table_name,
            'limit': limit
        }
        
        return self.fetch_data(query)


# 注册MongoDB数据源
DataSourceFactory.register("mongodb", MongoDBDataSource) 