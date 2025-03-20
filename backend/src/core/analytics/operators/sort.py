from typing import Dict, Any, List, Optional
import pandas as pd
from .base import Operator, OperatorFactory
from src.utils.exceptions import AnalyticsException
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("sort_operator")


class SortOperator(Operator):
    """排序操作"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化排序操作
        
        Args:
            params: 操作参数，包含dataset_name和sort_by
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
        
        if 'sort_by' not in self.params:
            logger.error("缺少参数: sort_by")
            return False
        
        # 检查sort_by是否为列表
        if not isinstance(self.params['sort_by'], list):
            logger.error("参数sort_by必须为列表")
            return False
        
        # 检查每个排序项
        for item in self.params['sort_by']:
            if not isinstance(item, dict):
                logger.error("排序项必须为字典")
                return False
            
            if 'column' not in item:
                logger.error("排序项缺少column字段")
                return False
            
            if 'ascending' in item and not isinstance(item['ascending'], bool):
                logger.error("排序项的ascending字段必须为布尔值")
                return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行排序操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("排序操作参数无效")
        
        # 获取参数
        dataset_name = self.params['dataset_name']
        sort_by = self.params['sort_by']
        output_name = self.params.get('output_name', f"{dataset_name}_sorted")
        
        # 检查数据集是否存在
        if dataset_name not in data:
            raise AnalyticsException(f"数据集不存在: {dataset_name}")
        
        # 获取数据集
        df = data[dataset_name]
        
        try:
            # 准备排序参数
            columns = []
            ascending = []
            
            for item in sort_by:
                column = item['column']
                
                # 检查列是否存在
                if column not in df.columns:
                    raise AnalyticsException(f"列不存在: {column}")
                
                columns.append(column)
                ascending.append(item.get('ascending', True))
            
            # 执行排序
            result = df.sort_values(by=columns, ascending=ascending).copy()
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"排序操作失败: {str(e)}")
            raise AnalyticsException(f"排序操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "sort",
            "display_name": "排序",
            "description": "对数据集进行排序",
            "params": [
                {
                    "name": "dataset_name",
                    "type": "string",
                    "description": "输入数据集名称",
                    "required": True
                },
                {
                    "name": "sort_by",
                    "type": "array",
                    "description": "排序条件列表",
                    "required": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "column": {
                                "type": "string",
                                "description": "列名"
                            },
                            "ascending": {
                                "type": "boolean",
                                "description": "是否升序",
                                "default": True
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
OperatorFactory.register("sort", SortOperator) 