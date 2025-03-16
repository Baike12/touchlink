from typing import Dict, Any, List, Optional
import pandas as pd
import uuid
import json
from datetime import datetime

from .operators import OperatorFactory
from backend.src.utils.exceptions import AnalyticsException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("analytics_pipeline")


class Pipeline:
    """分析流水线"""
    
    def __init__(self, name: str = None, description: str = None):
        """
        初始化分析流水线
        
        Args:
            name: 流水线名称
            description: 流水线描述
        """
        self.id = str(uuid.uuid4())
        self.name = name or f"Pipeline-{self.id[:8]}"
        self.description = description or ""
        self.steps = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_step(self, operator_type: str, params: Dict[str, Any]) -> 'Pipeline':
        """
        添加流水线步骤
        
        Args:
            operator_type: 操作类型
            params: 操作参数
            
        Returns:
            Pipeline: 流水线实例
        """
        # 检查操作类型是否存在
        if operator_type not in OperatorFactory.get_registered_operators():
            raise AnalyticsException(f"不支持的操作类型: {operator_type}")
        
        # 创建操作实例
        operator = OperatorFactory.create(operator_type, params)
        
        # 验证参数
        if not operator.validate_params():
            raise AnalyticsException(f"操作参数无效: {operator_type}")
        
        # 添加步骤
        self.steps.append({
            "id": str(uuid.uuid4()),
            "operator_type": operator_type,
            "params": params
        })
        
        # 更新时间
        self.updated_at = datetime.now()
        
        return self
    
    def execute(self, initial_data: Dict[str, pd.DataFrame] = None) -> Dict[str, pd.DataFrame]:
        """
        执行流水线
        
        Args:
            initial_data: 初始数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 执行结果，键为数据集名称，值为数据集
        """
        # 初始化数据
        data = initial_data or {}
        
        # 检查流水线是否为空
        if not self.steps:
            logger.warning("流水线为空")
            return data
        
        # 执行流水线
        for i, step in enumerate(self.steps):
            try:
                # 创建操作实例
                operator = OperatorFactory.create(step["operator_type"], step["params"])
                
                # 执行操作
                logger.info(f"执行步骤 {i+1}/{len(self.steps)}: {step['operator_type']}")
                step_result = operator.execute(data)
                
                # 更新数据
                data.update(step_result)
                
                logger.info(f"步骤 {i+1} 执行成功，生成数据集: {', '.join(step_result.keys())}")
            
            except Exception as e:
                logger.error(f"步骤 {i+1} 执行失败: {str(e)}")
                raise AnalyticsException(f"流水线执行失败，步骤 {i+1}: {str(e)}")
        
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            Dict[str, Any]: 流水线字典
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_json(self) -> str:
        """
        转换为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipeline':
        """
        从字典创建流水线
        
        Args:
            data: 流水线字典
            
        Returns:
            Pipeline: 流水线实例
        """
        pipeline = cls(name=data.get("name"), description=data.get("description"))
        pipeline.id = data.get("id", str(uuid.uuid4()))
        pipeline.steps = data.get("steps", [])
        
        # 解析时间
        if "created_at" in data:
            pipeline.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            pipeline.updated_at = datetime.fromisoformat(data["updated_at"])
        
        return pipeline
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Pipeline':
        """
        从JSON字符串创建流水线
        
        Args:
            json_str: JSON字符串
            
        Returns:
            Pipeline: 流水线实例
        """
        data = json.loads(json_str)
        return cls.from_dict(data) 