from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from .base import Operator, OperatorFactory
from backend.src.utils.exceptions import AnalyticsException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("filter_operator")


class FilterOperator(Operator):
    """过滤操作"""
    
    # 支持的操作符
    SUPPORTED_OPERATORS = {
        "eq": "==",
        "ne": "!=",
        "gt": ">",
        "ge": ">=",
        "lt": "<",
        "le": "<=",
        "in": "in",
        "not_in": "not in",
        "contains": "contains",
        "not_contains": "not contains",
        "starts_with": "startswith",
        "ends_with": "endswith",
        "is_null": "isnull",
        "is_not_null": "notnull"
    }
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化过滤操作
        
        Args:
            params: 操作参数，包含dataset_name和conditions
        """
        super().__init__(params)
    
    def validate_params(self) -> bool:
        """
        验证参数
        
        Returns:
            bool: 参数是否有效
        """
        # 检查必要参数
        if 'dataset_name' not in self.params:
            logger.error("缺少参数: dataset_name")
            return False
        
        if 'conditions' not in self.params:
            logger.error("缺少参数: conditions")
            return False
        
        # 检查conditions是否为列表
        if not isinstance(self.params['conditions'], list):
            logger.error("参数conditions必须为列表")
            return False
        
        # 检查每个条件
        for condition in self.params['conditions']:
            if not isinstance(condition, dict):
                logger.error("条件必须为字典")
                return False
            
            if 'column' not in condition:
                logger.error("条件缺少column字段")
                return False
            
            if 'operator' not in condition:
                logger.error("条件缺少operator字段")
                return False
            
            if condition['operator'] not in self.SUPPORTED_OPERATORS:
                logger.error(f"不支持的操作符: {condition['operator']}")
                return False
            
            # 对于需要值的操作符，检查value字段
            if condition['operator'] not in ['is_null', 'is_not_null']:
                if 'value' not in condition:
                    logger.error(f"操作符 {condition['operator']} 需要value字段")
                    return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行过滤操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("过滤操作参数无效")
        
        # 获取参数
        dataset_name = self.params['dataset_name']
        conditions = self.params['conditions']
        output_name = self.params.get('output_name', f"{dataset_name}_filtered")
        
        # 检查数据集是否存在
        if dataset_name not in data:
            raise AnalyticsException(f"数据集不存在: {dataset_name}")
        
        # 获取数据集
        df = data[dataset_name]
        
        try:
            # 应用过滤条件
            result = df.copy()
            
            for condition in conditions:
                column = condition['column']
                operator = condition['operator']
                
                # 检查列是否存在
                if column not in df.columns:
                    raise AnalyticsException(f"列不存在: {column}")
                
                # 根据操作符应用过滤条件
                if operator == 'eq':
                    result = result[result[column] == condition['value']]
                
                elif operator == 'ne':
                    result = result[result[column] != condition['value']]
                
                elif operator == 'gt':
                    result = result[result[column] > condition['value']]
                
                elif operator == 'ge':
                    result = result[result[column] >= condition['value']]
                
                elif operator == 'lt':
                    result = result[result[column] < condition['value']]
                
                elif operator == 'le':
                    result = result[result[column] <= condition['value']]
                
                elif operator == 'in':
                    result = result[result[column].isin(condition['value'])]
                
                elif operator == 'not_in':
                    result = result[~result[column].isin(condition['value'])]
                
                elif operator == 'contains':
                    result = result[result[column].astype(str).str.contains(str(condition['value']), na=False)]
                
                elif operator == 'not_contains':
                    result = result[~result[column].astype(str).str.contains(str(condition['value']), na=False)]
                
                elif operator == 'starts_with':
                    result = result[result[column].astype(str).str.startswith(str(condition['value']), na=False)]
                
                elif operator == 'ends_with':
                    result = result[result[column].astype(str).str.endswith(str(condition['value']), na=False)]
                
                elif operator == 'is_null':
                    result = result[result[column].isna()]
                
                elif operator == 'is_not_null':
                    result = result[~result[column].isna()]
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"过滤操作失败: {str(e)}")
            raise AnalyticsException(f"过滤操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "filter",
            "display_name": "过滤",
            "description": "根据条件过滤数据集",
            "params": [
                {
                    "name": "dataset_name",
                    "type": "string",
                    "description": "输入数据集名称",
                    "required": True
                },
                {
                    "name": "conditions",
                    "type": "array",
                    "description": "过滤条件列表",
                    "required": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "description": "列名"
                            },
                            "operator": {
                                "type": "string",
                                "description": "操作符",
                                "enum": list(cls.SUPPORTED_OPERATORS.keys())
                            },
                            "value": {
                                "type": "any",
                                "description": "比较值"
                            }
                        }
                    }
                },
                {
                    "name": "output_name",
                    "type": "string",
                    "description": "输出数据集名称",
                    "required": False
                }
            ]
        }


# 注册操作
OperatorFactory.register("filter", FilterOperator) 