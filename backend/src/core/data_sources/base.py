from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional


class DataSource(ABC):
    """
    数据源基类，定义所有数据源必须实现的接口
    """
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到数据源
        
        Args:
            config: 连接配置信息
            
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """
        断开与数据源的连接
        """
        pass
    
    @abstractmethod
    def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试数据源连接
        
        Args:
            config: 连接配置信息
            
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def get_tables(self) -> List[str]:
        """
        获取数据源中的所有表名
        
        Returns:
            List[str]: 表名列表
        """
        pass
    
    @abstractmethod
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取指定表的结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict[str, Any]]: 表结构信息，包含字段名、类型等
        """
        pass
    
    @abstractmethod
    def fetch_data(self, query: Dict[str, Any]) -> pd.DataFrame:
        """
        从数据源获取数据
        
        Args:
            query: 查询参数
            
        Returns:
            pd.DataFrame: 查询结果数据
        """
        pass
    
    @abstractmethod
    def get_sample_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        获取表的样本数据
        
        Args:
            table_name: 表名
            limit: 返回的最大行数
            
        Returns:
            pd.DataFrame: 样本数据
        """
        pass


class DataSourceFactory:
    """
    数据源工厂类，用于注册和创建数据源实例
    """
    _sources = {}
    
    @classmethod
    def register(cls, source_type: str, source_class) -> None:
        """
        注册数据源类
        
        Args:
            source_type: 数据源类型名称
            source_class: 数据源类
        """
        cls._sources[source_type] = source_class
    
    @classmethod
    def create(cls, source_type: str) -> Optional[DataSource]:
        """
        创建数据源实例
        
        Args:
            source_type: 数据源类型名称
            
        Returns:
            DataSource: 数据源实例，如果类型不存在则返回None
        """
        source_class = cls._sources.get(source_type)
        if source_class:
            return source_class()
        return None
    
    @classmethod
    def get_registered_sources(cls) -> List[str]:
        """
        获取所有已注册的数据源类型
        
        Returns:
            List[str]: 数据源类型列表
        """
        return list(cls._sources.keys()) 