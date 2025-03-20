from .base import DataSource, DataSourceFactory
from .mysql import MySQLDataSource
from .mongodb import MongoDBDataSource
from .excel import ExcelDataSource

# 确保所有数据源已注册
# 注册在各自的文件末尾已完成

# 注册数据源
DataSourceFactory.register("mysql", MySQLDataSource)
DataSourceFactory.register("excel", ExcelDataSource)

__all__ = ['DataSource', 'DataSourceFactory', 'MySQLDataSource', 'MongoDBDataSource', 'ExcelDataSource'] 