from typing import Dict, Any, List, Optional
import pandas as pd
from .base import Operator, OperatorFactory
from backend.src.utils.exceptions import AnalyticsException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("union_operator")


class UnionOperator(Operator):
    """联合查询操作"""
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化联合查询操作
        
        Args:
            params: 操作参数，包含datasets
        """
        super().__init__(params)
    
    def validate_params(self) -> bool:
        """
        验证参数
        
        Returns:
            bool: 参数是否有效
        """
        # 检查必要参数
        if 'datasets' not in self.params:
            logger.error("缺少参数: datasets")
            return False
        
        # 检查datasets是否为列表
        if not isinstance(self.params['datasets'], list):
            logger.error("参数datasets必须为列表")
            return False
        
        # 检查datasets是否至少包含两个数据集
        if len(self.params['datasets']) < 2:
            logger.error("参数datasets必须至少包含两个数据集")
            return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行联合查询操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("联合查询操作参数无效")
        
        # 获取参数
        datasets = self.params['datasets']
        ignore_index = self.params.get('ignore_index', True)
        output_name = self.params.get('output_name', "union_result")
        
        try:
            # 检查数据集是否存在
            dfs = []
            for dataset_name in datasets:
                if dataset_name not in data:
                    raise AnalyticsException(f"数据集不存在: {dataset_name}")
                dfs.append(data[dataset_name])
            
            # 执行联合查询
            result = pd.concat(dfs, ignore_index=ignore_index)
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"联合查询操作失败: {str(e)}")
            raise AnalyticsException(f"联合查询操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "union",
            "display_name": "联合查询",
            "description": "将多个数据集合并为一个数据集",
            "params": [
                {
                    "name": "datasets",
                    "type": "array",
                    "description": "数据集名称列表",
                    "required": True
                },
                {
                    "name": "ignore_index",
                    "type": "boolean",
                    "description": "是否忽略原索引",
                    "required": False,
                    "default": True
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
OperatorFactory.register("union", UnionOperator) 