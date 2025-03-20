from typing import Dict, Any, List, Optional
import pandas as pd
from .base import Operator, OperatorFactory
from src.utils.exceptions import AnalyticsException
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("column_select_operator")


class ColumnSelectOperator(Operator):
    """列选择操作"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化列选择操作
        
        Args:
            params: 操作参数，包含dataset_name和columns
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
        
        if 'columns' not in self.params:
            logger.error("缺少参数: columns")
            return False
        
        # 检查columns是否为列表
        if not isinstance(self.params['columns'], list):
            logger.error("参数columns必须为列表")
            return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行列选择操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("列选择操作参数无效")
        
        # 获取参数
        dataset_name = self.params['dataset_name']
        columns = self.params['columns']
        output_name = self.params.get('output_name', f"{dataset_name}_selected")
        
        # 检查数据集是否存在
        if dataset_name not in data:
            raise AnalyticsException(f"数据集不存在: {dataset_name}")
        
        # 获取数据集
        df = data[dataset_name]
        
        # 检查列是否存在
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise AnalyticsException(f"列不存在: {', '.join(missing_columns)}")
        
        try:
            # 选择列
            result = df[columns].copy()
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"列选择操作失败: {str(e)}")
            raise AnalyticsException(f"列选择操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "column_select",
            "display_name": "列选择",
            "description": "从数据集中选择指定的列",
            "params": [
                {
                    "name": "dataset_name",
                    "type": "string",
                    "description": "输入数据集名称",
                    "required": True
                },
                {
                    "name": "columns",
                    "type": "array",
                    "description": "要选择的列名列表",
                    "required": True
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
OperatorFactory.register("column_select", ColumnSelectOperator) 