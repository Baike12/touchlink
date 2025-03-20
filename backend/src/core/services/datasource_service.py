from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import base64
from cryptography.fernet import Fernet

from src.core.models import DataSource
from src.core.data_sources import DataSourceFactory
from src.utils.exceptions import NotFoundException, DataSourceException
from src.config.settings import settings
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("datasource_service")

# 创建加密密钥
def get_fernet_key(key):
    """确保密钥是有效的Fernet密钥格式"""
    try:
        # 尝试直接使用密钥
        return Fernet(key.encode())
    except Exception as e:
        logger.warning(f"无法直接使用密钥作为Fernet密钥: {str(e)}")
        # 如果失败，生成一个基于密钥的新Fernet密钥
        key_bytes = key.encode()
        # 使用SHA-256哈希确保长度正确
        import hashlib
        hashed = hashlib.sha256(key_bytes).digest()
        # 转换为Base64编码
        encoded = base64.urlsafe_b64encode(hashed)
        logger.info("已生成基于配置的Fernet密钥")
        return Fernet(encoded)

# 使用配置文件中的SECRET_KEY
fernet = get_fernet_key(settings.SECRET_KEY)


class DataSourceService:
    """数据源服务"""
    
    @staticmethod
    def create_datasource(db: Session, name: str, type: str, config: Dict[str, Any]) -> DataSource:
        """
        创建数据源
        
        Args:
            db: 数据库会话
            name: 数据源名称
            type: 数据源类型
            config: 数据源配置
            
        Returns:
            DataSource: 创建的数据源
        """
        # 加密配置信息
        encrypted_config = DataSourceService._encrypt_config(config)
        
        # 创建数据源
        datasource = DataSource(
            name=name,
            type=type,
            config=encrypted_config
        )
        
        # 保存到数据库
        db.add(datasource)
        db.commit()
        db.refresh(datasource)
        
        logger.info(f"创建数据源: {datasource.id}, 类型: {datasource.type}, 名称: {datasource.name}")
        return datasource
    
    @staticmethod
    def get_datasource(db: Session, datasource_id: str) -> DataSource:
        """
        获取数据源
        
        Args:
            db: 数据库会话
            datasource_id: 数据源ID
            
        Returns:
            DataSource: 数据源
            
        Raises:
            NotFoundException: 数据源不存在
        """
        datasource = db.query(DataSource).filter(DataSource.id == datasource_id).first()
        if not datasource:
            raise NotFoundException(f"数据源不存在: {datasource_id}")
        
        return datasource
    
    @staticmethod
    def get_user_datasources(db: Session, user_id: str) -> List[DataSource]:
        """
        获取用户的所有数据源
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[DataSource]: 数据源列表
        """
        return db.query(DataSource).filter(DataSource.user_id == user_id).all()
    
    @staticmethod
    def update_datasource(db: Session, datasource_id: str, name: Optional[str] = None, 
                         config: Optional[Dict[str, Any]] = None) -> DataSource:
        """
        更新数据源
        
        Args:
            db: 数据库会话
            datasource_id: 数据源ID
            name: 数据源名称
            config: 数据源配置
            
        Returns:
            DataSource: 更新后的数据源
            
        Raises:
            NotFoundException: 数据源不存在
        """
        # 获取数据源
        datasource = DataSourceService.get_datasource(db, datasource_id)
        
        # 更新名称
        if name:
            datasource.name = name
        
        # 更新配置
        if config:
            datasource.config = DataSourceService._encrypt_config(config)
        
        # 保存到数据库
        db.commit()
        db.refresh(datasource)
        
        logger.info(f"更新数据源: {datasource.id}")
        return datasource
    
    @staticmethod
    def delete_datasource(db: Session, datasource_id: str) -> None:
        """
        删除数据源
        
        Args:
            db: 数据库会话
            datasource_id: 数据源ID
            
        Raises:
            NotFoundException: 数据源不存在
        """
        # 获取数据源
        datasource = DataSourceService.get_datasource(db, datasource_id)
        
        # 删除数据源
        db.delete(datasource)
        db.commit()
        
        logger.info(f"删除数据源: {datasource_id}")
    
    @staticmethod
    def test_connection(type: str, config: Dict[str, Any]) -> bool:
        """
        测试数据源连接
        
        Args:
            type: 数据源类型
            config: 数据源配置
            
        Returns:
            bool: 连接是否成功
            
        Raises:
            DataSourceException: 数据源类型不支持
        """
        # 创建数据源实例
        datasource = DataSourceFactory.create(type)
        if not datasource:
            raise DataSourceException(f"不支持的数据源类型: {type}")
        
        # 测试连接
        return datasource.test_connection(config)
    
    @staticmethod
    def connect_datasource(datasource_id: str, db: Session) -> Any:
        """
        连接数据源
        
        Args:
            datasource_id: 数据源ID
            db: 数据库会话
            
        Returns:
            Any: 数据源连接实例
            
        Raises:
            NotFoundException: 数据源不存在
            DataSourceException: 数据源类型不支持或连接失败
        """
        # 获取数据源
        datasource = DataSourceService.get_datasource(db, datasource_id)
        
        # 解密配置
        config = DataSourceService._decrypt_config(datasource.config)
        
        # 创建数据源实例
        source = DataSourceFactory.create(datasource.type)
        if not source:
            raise DataSourceException(f"不支持的数据源类型: {datasource.type}")
        
        # 连接数据源
        success = source.connect(config)
        if not success:
            raise DataSourceException(f"连接数据源失败: {datasource.name}")
        
        logger.info(f"连接数据源: {datasource.id}, 类型: {datasource.type}, 名称: {datasource.name}")
        return source
    
    @staticmethod
    def get_tables(datasource_id: str, db: Session) -> List[str]:
        """
        获取数据源中的表列表
        
        Args:
            datasource_id: 数据源ID
            db: 数据库会话
            
        Returns:
            List[str]: 表名列表
            
        Raises:
            NotFoundException: 数据源不存在
            DataSourceException: 数据源类型不支持或连接失败
        """
        # 连接数据源
        source = DataSourceService.connect_datasource(datasource_id, db)
        
        # 获取表列表
        return source.get_tables()
    
    @staticmethod
    def get_table_schema(datasource_id: str, table_name: str, db: Session) -> List[Dict[str, Any]]:
        """
        获取表结构
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            db: 数据库会话
            
        Returns:
            List[Dict[str, Any]]: 表结构
            
        Raises:
            NotFoundException: 数据源不存在
            DataSourceException: 数据源类型不支持或连接失败
        """
        # 连接数据源
        source = DataSourceService.connect_datasource(datasource_id, db)
        
        # 获取表结构
        return source.get_table_schema(table_name)
    
    @staticmethod
    def get_sample_data(datasource_id: str, table_name: str, limit: int, db: Session) -> Dict[str, Any]:
        """
        获取表的样本数据
        
        Args:
            datasource_id: 数据源ID
            table_name: 表名
            limit: 返回的最大行数
            db: 数据库会话
            
        Returns:
            Dict[str, Any]: 样本数据
            
        Raises:
            NotFoundException: 数据源不存在
            DataSourceException: 数据源类型不支持或连接失败
        """
        # 连接数据源
        source = DataSourceService.connect_datasource(datasource_id, db)
        
        # 获取样本数据
        df = source.get_sample_data(table_name, limit)
        
        # 转换为字典
        return {
            "columns": df.columns.tolist(),
            "data": df.to_dict(orient="records")
        }
    
    @staticmethod
    def _encrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        加密配置信息
        
        Args:
            config: 配置信息
            
        Returns:
            Dict[str, Any]: 加密后的配置信息
        """
        # 复制配置
        encrypted_config = config.copy()
        
        # 加密敏感信息
        if "password" in encrypted_config:
            encrypted_config["password"] = fernet.encrypt(encrypted_config["password"].encode()).decode()
        
        return encrypted_config
    
    @staticmethod
    def _decrypt_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        解密配置信息
        
        Args:
            config: 加密的配置信息
            
        Returns:
            Dict[str, Any]: 解密后的配置信息
        """
        # 复制配置
        decrypted_config = config.copy()
        
        # 解密敏感信息
        if "password" in decrypted_config:
            decrypted_config["password"] = fernet.decrypt(decrypted_config["password"].encode()).decode()
        
        return decrypted_config
    
    @staticmethod
    def get_all_datasources(db: Session) -> List[DataSource]:
        """
        获取所有数据源
        
        Args:
            db: 数据库会话
            
        Returns:
            List[DataSource]: 数据源列表
        """
        return db.query(DataSource).all() 