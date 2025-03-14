from typing import Dict, Any, List, Optional
import pandas as pd
from .base import Operator, OperatorFactory
from src.utils.exceptions import AnalyticsException
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("join_operator")


class JoinOperator(Operator):
    """表连接操作"""
    
    # 支持的连接类型
    SUPPORTED_JOIN_TYPES = {
        "inner": "inner",
        "left": "left",
        "right": "right",
        "outer": "outer",
        "cross": "cross"
    }
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        初始化表连接操作
        
        Args:
            params: 操作参数，包含left_dataset, right_dataset, join_type和on
        """
        super().__init__(params)
    
    def validate_params(self) -> bool:
        """
        验证参数
        
        Returns:
            bool: 参数是否有效
        """
        # 检查必要参数
        if 'left_dataset' not in self.params:
            logger.error("缺少参数: left_dataset")
            return False
        
        if 'right_dataset' not in self.params:
            logger.error("缺少参数: right_dataset")
            return False
        
        if 'join_type' not in self.params:
            logger.error("缺少参数: join_type")
            return False
        
        # 检查连接类型
        if self.params['join_type'] not in self.SUPPORTED_JOIN_TYPES:
            logger.error(f"不支持的连接类型: {self.params['join_type']}")
            return False
        
        # 对于非交叉连接，检查连接条件
        if self.params['join_type'] != 'cross':
            if 'on' not in self.params and 'left_on' not in self.params and 'right_on' not in self.params:
                logger.error("缺少连接条件: on 或 left_on/right_on")
                return False
            
            # 如果使用on，检查是否为字符串或列表
            if 'on' in self.params:
                if not isinstance(self.params['on'], (str, list)):
                    logger.error("参数on必须为字符串或列表")
                    return False
            
            # 如果使用left_on/right_on，检查是否为字符串或列表，且两者都存在
            if 'left_on' in self.params or 'right_on' in self.params:
                if 'left_on' not in self.params:
                    logger.error("使用right_on时必须同时指定left_on")
                    return False
                
                if 'right_on' not in self.params:
                    logger.error("使用left_on时必须同时指定right_on")
                    return False
                
                if not isinstance(self.params['left_on'], (str, list)):
                    logger.error("参数left_on必须为字符串或列表")
                    return False
                
                if not isinstance(self.params['right_on'], (str, list)):
                    logger.error("参数right_on必须为字符串或列表")
                    return False
                
                # 如果是列表，检查长度是否相同
                if isinstance(self.params['left_on'], list) and isinstance(self.params['right_on'], list):
                    if len(self.params['left_on']) != len(self.params['right_on']):
                        logger.error("参数left_on和right_on的长度必须相同")
                        return False
        
        return True
    
    def execute(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        执行表连接操作
        
        Args:
            data: 输入数据，键为数据集名称，值为数据集
            
        Returns:
            Dict[str, pd.DataFrame]: 输出数据，键为数据集名称，值为数据集
        """
        # 验证参数
        if not self.validate_params():
            raise AnalyticsException("表连接操作参数无效")
        
        # 获取参数
        left_dataset = self.params['left_dataset']
        right_dataset = self.params['right_dataset']
        join_type = self.params['join_type']
        output_name = self.params.get('output_name', f"{left_dataset}_{right_dataset}_joined")
        
        # 检查数据集是否存在
        if left_dataset not in data:
            raise AnalyticsException(f"左侧数据集不存在: {left_dataset}")
        
        if right_dataset not in data:
            raise AnalyticsException(f"右侧数据集不存在: {right_dataset}")
        
        # 获取数据集
        left_df = data[left_dataset]
        right_df = data[right_dataset]
        
        try:
            # 准备连接参数
            join_params = {
                "how": self.SUPPORTED_JOIN_TYPES[join_type]
            }
            
            # 设置连接条件
            if 'on' in self.params:
                join_params['on'] = self.params['on']
            elif 'left_on' in self.params and 'right_on' in self.params:
                join_params['left_on'] = self.params['left_on']
                join_params['right_on'] = self.params['right_on']
            
            # 设置后缀
            suffixes = self.params.get('suffixes', ['_x', '_y'])
            join_params['suffixes'] = suffixes
            
            # 执行连接
            result = pd.merge(left_df, right_df, **join_params)
            
            # 返回结果
            return {output_name: result}
        
        except Exception as e:
            logger.error(f"表连接操作失败: {str(e)}")
            raise AnalyticsException(f"表连接操作失败: {str(e)}")
    
    @classmethod
    def get_operator_info(cls) -> Dict[str, Any]:
        """
        获取操作信息
        
        Returns:
            Dict[str, Any]: 操作信息，包含名称、描述、参数等
        """
        return {
            "name": "join",
            "display_name": "表连接",
            "description": "连接两个数据集",
            "params": [
                {
                    "name": "left_dataset",
                    "type": "string",
                    "description": "左侧数据集名称",
                    "required": True
                },
                {
                    "name": "right_dataset",
                    "type": "string",
                    "description": "右侧数据集名称",
                    "required": True
                },
                {
                    "name": "join_type",
                    "type": "string",
                    "description": "连接类型",
                    "required": True,
                    "enum": list(cls.SUPPORTED_JOIN_TYPES.keys())
                },
                {
                    "name": "on",
                    "type": ["string", "array"],
                    "description": "连接列名",
                    "required": False
                },
                {
                    "name": "left_on",
                    "type": ["string", "array"],
                    "description": "左侧连接列名",
                    "required": False
                },
                {
                    "name": "right_on",
                    "type": ["string", "array"],
                    "description": "右侧连接列名",
                    "required": False
                },
                {
                    "name": "suffixes",
                    "type": "array",
                    "description": "重复列名后缀",
                    "required": False,
                    "default": ["_x", "_y"]
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
OperatorFactory.register("join", JoinOperator) 