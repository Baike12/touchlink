import pandas as pd
import os
from typing import Dict, Any, List, Optional
from .base import DataSource, DataSourceFactory
from src.utils.exceptions import DataSourceException
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("excel_datasource")


class ExcelDataSource(DataSource):
    """Excel数据源实现"""
    
    def __init__(self):
        """初始化Excel数据源"""
        self.file_path = None
        self.excel_file = None
        self.sheets = {}
        self.connection_config = None
    
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        连接到Excel文件
        
        Args:
            config: 连接配置，包含file_path等
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 获取文件路径
            file_path = config.get('file_path')
            if not file_path:
                raise DataSourceException("配置中缺少file_path参数")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise DataSourceException(f"文件不存在: {file_path}")
            
            # 检查文件是否为Excel文件
            if not file_path.endswith(('.xls', '.xlsx', '.xlsm')):
                raise DataSourceException(f"不支持的文件类型: {file_path}")
            
            # 读取Excel文件
            self.excel_file = pd.ExcelFile(file_path)
            
            # 获取所有工作表
            sheet_names = self.excel_file.sheet_names
            
            # 保存文件路径
            self.file_path = file_path
            
            # 保存连接配置
            self.connection_config = config
            
            logger.info(f"成功连接到Excel文件: {file_path}, 共{len(sheet_names)}个工作表")
            return True
        
        except Exception as e:
            logger.error(f"连接Excel文件失败: {str(e)}")
            raise DataSourceException(f"连接Excel文件失败: {str(e)}")
    
    def disconnect(self) -> None:
        """断开与Excel文件的连接"""
        if self.excel_file:
            self.excel_file.close()
            self.excel_file = None
            self.file_path = None
            self.sheets = {}
            logger.info("已断开Excel文件连接")
    
    def test_connection(self, config: Dict[str, Any]) -> bool:
        """
        测试Excel文件连接
        
        Args:
            config: 连接配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            # 获取文件路径
            file_path = config.get('file_path')
            if not file_path:
                logger.error("配置中缺少file_path参数")
                return False
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return False
            
            # 检查文件是否为Excel文件
            if not file_path.endswith(('.xls', '.xlsx', '.xlsm')):
                logger.error(f"不支持的文件类型: {file_path}")
                return False
            
            # 尝试读取Excel文件
            with pd.ExcelFile(file_path) as excel_file:
                sheet_names = excel_file.sheet_names
            
            logger.info(f"Excel连接测试成功: {file_path}, 共{len(sheet_names)}个工作表")
            return True
        
        except Exception as e:
            logger.error(f"Excel连接测试失败: {str(e)}")
            return False
    
    def get_tables(self) -> List[str]:
        """
        获取Excel文件中的所有工作表名
        
        Returns:
            List[str]: 工作表名列表
        """
        if not self.excel_file:
            raise DataSourceException("未连接到Excel文件")
        
        try:
            sheet_names = self.excel_file.sheet_names
            logger.debug(f"获取到{len(sheet_names)}个工作表")
            return sheet_names
        
        except Exception as e:
            logger.error(f"获取工作表列表失败: {str(e)}")
            raise DataSourceException(f"获取工作表列表失败: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        获取指定工作表的结构信息
        
        Args:
            table_name: 工作表名
            
        Returns:
            List[Dict[str, Any]]: 工作表结构信息，包含字段名、类型等
        """
        if not self.excel_file:
            raise DataSourceException("未连接到Excel文件")
        
        try:
            # 检查工作表是否存在
            if table_name not in self.excel_file.sheet_names:
                raise DataSourceException(f"工作表不存在: {table_name}")
            
            # 读取工作表
            df = self.excel_file.parse(table_name, nrows=1)
            
            # 如果DataFrame为空，返回空列表
            if df.empty:
                return []
            
            # 分析工作表结构
            schema = []
            for column in df.columns:
                schema.append({
                    "name": str(column),
                    "type": str(df[column].dtype),
                    "nullable": True,
                    "default": None,
                    "primary_key": False
                })
            
            logger.debug(f"获取工作表{table_name}的结构信息，共{len(schema)}列")
            return schema
        
        except Exception as e:
            logger.error(f"获取工作表{table_name}的结构信息失败: {str(e)}")
            raise DataSourceException(f"获取工作表{table_name}的结构信息失败: {str(e)}")
    
    def fetch_data(self, query: Dict[str, Any]) -> pd.DataFrame:
        """
        从Excel文件获取数据
        
        Args:
            query: 查询参数，包含sheet_name, usecols, skiprows, nrows等
            
        Returns:
            pd.DataFrame: 查询结果数据
        """
        if not self.excel_file:
            raise DataSourceException("未连接到Excel文件")
        
        try:
            # 获取工作表名
            sheet_name = query.get('sheet_name')
            if not sheet_name:
                raise DataSourceException("查询参数必须包含sheet_name")
            
            # 检查工作表是否存在
            if sheet_name not in self.excel_file.sheet_names:
                raise DataSourceException(f"工作表不存在: {sheet_name}")
            
            # 构建查询参数
            usecols = query.get('usecols', None)
            skiprows = query.get('skiprows', None)
            nrows = query.get('nrows', None)
            
            # 读取工作表
            df = self.excel_file.parse(
                sheet_name=sheet_name,
                usecols=usecols,
                skiprows=skiprows,
                nrows=nrows
            )
            
            logger.debug(f"从工作表{sheet_name}获取数据，共{len(df)}行")
            return df
        
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise DataSourceException(f"执行查询失败: {str(e)}")
    
    def get_sample_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        获取工作表的样本数据
        
        Args:
            table_name: 工作表名
            limit: 返回的最大行数
            
        Returns:
            pd.DataFrame: 样本数据
        """
        query = {
            'sheet_name': table_name,
            'nrows': limit
        }
        
        return self.fetch_data(query)


# 注册Excel数据源
DataSourceFactory.register("excel", ExcelDataSource) 