from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("analytics_operators")


class Operator(ABC):
    """分析操作基类"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化操作
        
        Args:
            params: 操作参数
        """
        self.params = params or {}
    
    @abstractmethod
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        pass
    
    @abstractmethod
    def validate_params(self) -> bool:
        """
        验证参数
        
        Returns:
            bool: 参数是否有效
        """
        pass
    
    @classmethod
    @abstractmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        pass


class OperatorFactory:
    """操作工厂类"""
    _operators = {}
    
    @classmethod
    def register(cls, operator_type: str, operator_class) -> None:
        """
        注册操作类
        
        Args:
            operator_type: 操作类型名称
            operator_class: 操作类
        """
        cls._operators[operator_type] = operator_class
        logger.info(f"注册操作类: {operator_type}")
    
    @classmethod
    def create(cls, operator_type: str, params: Dict[str, Any] = None) -> Optional[Operator]:
        """
        创建操作实例
        
        Args:
            operator_type: 操作类型名称
            params: 操作参数
            
        Returns:
            Operator: 操作实例，如果类型不存在则返回None
        """
        operator_class = cls._operators.get(operator_type)
        if operator_class:
            return operator_class(params)
        return None
    
    @classmethod
    def get_registered_operators(cls) -> List[str]:
        """
        获取所有已注册的操作类型
        
        Returns:
            List[str]: 操作类型列表
        """
        return list(cls._operators.keys())
    
    @classmethod
    def get_operator_info(cls, operator_type: str) -> Optional[Dict[str, Any]]:
        """
        获取操作信息
        
        Args:
            operator_type: 操作类型名称
            
        Returns:
            Dict[str, Any]: 操作信息，如果类型不存在则返回None
        """
        operator_class = cls._operators.get(operator_type)
        if operator_class:
            return operator_class.get_operator_info()
        return None
    
    @classmethod
    def get_all_operator_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        获取所有操作信息
        
        Returns:
            Dict[str, Dict[str, Any]]: 操作信息字典，键为操作类型名称，值为操作信息
        """
        return {
            operator_type: operator_class.get_operator_info()
            for operator_type, operator_class in cls._operators.items()
        } 