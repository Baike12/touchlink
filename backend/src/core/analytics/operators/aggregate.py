from typing import Dict, Any, List, Optional
import pandas as pd
from .base import Operator, OperatorFactory
from backend.src.utils.exceptions import AnalyticsException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("aggregate_operator")


class AggregateOperator(Operator):
    """聚合操作"""
    
    # 支持的聚合函数
    SUPPORTED_AGGREGATIONS = {
        "sum": "sum",
        "avg": "mean",
        "min": "min",
        "max": "max",
        "count": "count",
        "distinct_count": "nunique",
        "median": "median",
        "std": "std",
        "var": "var",
        "first": "first",
        "last": "last"
    }
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化聚合操作
        
        Args:
            params: 操作参数，包含dataset_name, group_by和aggregations
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
        
        if 'group_by' not in self.params:
            logger.error("缺少参数: group_by")
            return False
        
        if 'aggregations' not in self.params:
            logger.error("缺少参数: aggregations")
            return False
        
        # 检查group_by是否为列表
        if not isinstance(self.params['group_by'], list):
            logger.error("参数group_by必须为列表")
            return False
        
        # 检查aggregations是否为列表
        if not isinstance(self.params['aggregations'], list):
            logger.error("参数aggregations必须为列表")
            return False
        
        # 检查每个聚合项
        for item in self.params['aggregations']:
            if not isinstance(item, dict):
                logger.error("聚合项必须为字典")
                return False
            
            if 'column' not in item:
                logger.error("聚合项缺少column字段")
                return False
            
            if 'function' not in item:
                logger.error("聚合项缺少function字段")
                return False
            
            if item['function'] not in self.SUPPORTED_AGGREGATIONS:
                logger.error(f"不支持的聚合函数: {item['function']}")
                return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行聚合操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("聚合操作参数无效")
        
        # 获取参数
        dataset_name = self.params['dataset_name']
        group_by = self.params['group_by']
        aggregations = self.params['aggregations']
        output_name = self.params.get('output_name', f"{dataset_name}_aggregated")
        
        # 检查数据集是否存在
        if dataset_name not in data:
            raise AnalyticsException(f"数据集不存在: {dataset_name}")
        
        # 获取数据集
        df = data[dataset_name]
        
        try:
            # 检查分组列是否存在
            for column in group_by:
                if column not in df.columns:
                    raise AnalyticsException(f"分组列不存在: {column}")
            
            # 准备聚合参数
            agg_dict = {}
            
            for item in aggregations:
                column = item['column']
                function = item['function']
                alias = item.get('alias', f"{column}_{function}")
                
                # 检查列是否存在
                if column not in df.columns:
                    raise AnalyticsException(f"聚合列不存在: {column}")
                
                # 添加到聚合字典
                agg_dict[alias] = pd.NamedAgg(
                    column=column,
                    aggfunc=self.SUPPORTED_AGGREGATIONS[function]
                )
            
            # 执行聚合
            if group_by:
                result = df.groupby(group_by, as_index=False).agg(**agg_dict)
            else:
                # 如果没有分组列，则对整个数据集聚合
                result = pd.DataFrame({
                    alias: [df[item['column']].agg(self.SUPPORTED_AGGREGATIONS[item['function']])]
                    for item in aggregations
                    for alias in [item.get('alias', f"{item['column']}_{item['function']}")]
                })
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"聚合操作失败: {str(e)}")
            raise AnalyticsException(f"聚合操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "aggregate",
            "display_name": "聚合",
            "description": "对数据集进行聚合计算",
            "params": [
                {
                    "name": "dataset_name",
                    "type": "string",
                    "description": "输入数据集名称",
                    "required": True
                },
                {
                    "name": "group_by",
                    "type": "array",
                    "description": "分组列列表",
                    "required": True
                },
                {
                    "name": "aggregations",
                    "type": "array",
                    "description": "聚合操作列表",
                    "required": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "description": "列名"
                            },
                            "function": {
                                "type": "string",
                                "description": "聚合函数",
                                "enum": list(cls.SUPPORTED_AGGREGATIONS.keys())
                            },
                            "alias": {
                                "type": "string",
                                "description": "结果列名",
                                "required": False
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
OperatorFactory.register("aggregate", AggregateOperator) 