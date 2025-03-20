import pandas as pd
import sqlalchemy
from typing import Dict, Any, List
import os
from .base import DataSource
from src.utils.logger import setup_logger
from src.config.database import get_user_database_url

logger = setup_logger("excel_datasource")

class ExcelDataSource(DataSource):
    """Excel数据源处理类"""
    
    def __init__(self):
        self.engine = None
        self.file_path = None
        self.table_name = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到Excel文件并导入到MySQL
        
        Args:
            config: 连接配置信息，包含：
                - file_path: Excel文件路径
                - table_name: 要创建的MySQL表名
                
        Returns:
            bool: 连接是否成功
        """
        try:
            self.file_path = config.get('file_path')
            self.table_name = config.get('table_name')
            
            if not self.file_path or not self.table_name:
                logger.error("缺少必要的配置信息")
                return False
            
            if not os.path.exists(self.file_path):
                logger.error(f"文件不存在: {self.file_path}")
                return False
            
            # 读取Excel文件
            df = pd.read_excel(self.file_path)
            
            # 连接到user_database
            self.engine = sqlalchemy.create_engine(get_user_database_url())
            
            # 将DataFrame导入到MySQL，添加自增ID列
            df.to_sql(
                name=self.table_name,
                con=self.engine,
                if_exists='replace',  # 如果表存在则替换
                index=True,  # 使用DataFrame的索引作为ID列
                index_label='id'  # ID列的名称
            )
            
            logger.info(f"Excel文件 {self.file_path} 已成功导入到MySQL表 {self.table_name}")
            return True
            
        except Exception as e:
            logger.error(f"连接Excel数据源失败: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开与数据源的连接"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
    
    def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试Excel文件是否可以正确读取
        
        Args:
            config: 连接配置信息
            
        Returns:
            bool: 测试是否成功
        """
        try:
            file_path = config.get('file_path')
            if not file_path or not os.path.exists(file_path):
                return False
            
            # 尝试读取Excel文件
            pd.read_excel(file_path)
            return True
            
        except Exception as e:
            logger.error(f"测试Excel数据源连接失败: {str(e)}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        获取已导入的MySQL表名
        
        Returns:
            List[str]: 表名列表
        """
        if not self.engine:
            return []
        
        inspector = sqlalchemy.inspect(self.engine)
        return inspector.get_table_names()
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            List[Dict[str, Any]]: 表结构信息
        """
        if not self.engine:
            return []
        
        inspector = sqlalchemy.inspect(self.engine)
        columns = inspector.get_columns(table_name)
        
        return [
            {
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column["nullable"]
            }
            for column in columns
        ]
    
    def get_sample_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        获取表的样本数据
        
        Args:
            table_name: 表名
            limit: 返回的最大行数
            
        Returns:
            pd.DataFrame: 样本数据
        """
        if not self.engine:
            return pd.DataFrame()
        
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return pd.read_sql(query, self.engine) 