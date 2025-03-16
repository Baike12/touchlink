from typing import Dict, Any, List, Optional
import pandas as pd
import json
import os
import uuid
from datetime import datetime

from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("chart_service")

# 支持的图表类型
CHART_TYPES = [
    "bar",      # 柱状图
    "line",     # 折线图
    "pie",      # 饼图
    "scatter",  # 散点图
    "area",     # 面积图
    "table"     # 表格
]

# 图表配置目录
CHART_DIR = "charts"
os.makedirs(CHART_DIR, exist_ok=True)


class ChartService:
    """图表服务"""
    
    # 添加类属性，方便访问
    CHART_TYPES = CHART_TYPES
    
    @staticmethod
    def validate_chart_config(chart_type: str, config: Dict[str, Any]) -> bool:
        """
        验证图表配置
        
        Args:
            chart_type: 图表类型
            config: 图表配置
            
        Returns:
            bool: 配置是否有效
        """
        # 检查图表类型
        if chart_type not in CHART_TYPES:
            logger.error(f"不支持的图表类型: {chart_type}")
            return False
        
        # 简化验证逻辑，只检查图表类型是否支持
        # 其他配置在生成图表时再处理
        return True
    
    @staticmethod
    def generate_chart_options(
        chart_type: str,
        data: pd.DataFrame,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成图表选项
        
        Args:
            chart_type: 图表类型
            data: 数据
            config: 图表配置
            
        Returns:
            Dict[str, Any]: 图表选项
        """
        # 基本选项
        options = {
            "title": {
                "text": config.get("title", "")
            },
            "tooltip": {
                "trigger": "axis" if chart_type in ["bar", "line", "area"] else "item"
            },
            "legend": {
                "data": []
            }
        }
        
        # 根据图表类型生成特定选项
        if chart_type in ["bar", "line", "area"]:
            # 获取X轴字段
            x_field = config.get("xAxis", {}).get("field")
            if not x_field or x_field not in data.columns:
                raise ValueError(f"X轴字段不存在: {x_field}")
            
            # 获取X轴数据
            x_data = data[x_field].tolist()
            
            # 设置X轴
            options["xAxis"] = {
                "type": "category",
                "data": x_data,
                "name": config.get("xAxis", {}).get("name", x_field)
            }
            
            # 设置Y轴
            options["yAxis"] = {
                "type": "value",
                "name": config.get("yAxis", {}).get("name", "")
            }
            
            # 设置系列
            options["series"] = []
            for series_config in config.get("series", []):
                y_field = series_config.get("field")
                if not y_field or y_field not in data.columns:
                    continue
                
                # 获取Y轴数据
                y_data = data[y_field].tolist()
                
                # 添加系列
                series = {
                    "name": series_config.get("name", y_field),
                    "type": chart_type,
                    "data": y_data
                }
                
                # 添加特定配置
                if chart_type == "area":
                    series["areaStyle"] = {}
                
                options["series"].append(series)
                options["legend"]["data"].append(series_config.get("name", y_field))
        
        elif chart_type == "pie":
            # 设置系列
            options["series"] = []
            for series_config in config.get("series", []):
                name_field = series_config.get("nameField")
                value_field = series_config.get("valueField")
                
                if not name_field or not value_field or name_field not in data.columns or value_field not in data.columns:
                    continue
                
                # 获取数据
                pie_data = []
                for _, row in data.iterrows():
                    pie_data.append({
                        "name": row[name_field],
                        "value": row[value_field]
                    })
                
                # 添加系列
                series = {
                    "name": series_config.get("name", ""),
                    "type": "pie",
                    "radius": series_config.get("radius", "60%"),
                    "data": pie_data
                }
                
                options["series"].append(series)
        
        elif chart_type == "scatter":
            # 设置X轴
            options["xAxis"] = {
                "type": "value",
                "name": config.get("xAxis", {}).get("name", "")
            }
            
            # 设置Y轴
            options["yAxis"] = {
                "type": "value",
                "name": config.get("yAxis", {}).get("name", "")
            }
            
            # 设置系列
            options["series"] = []
            for series_config in config.get("series", []):
                x_field = series_config.get("xField")
                y_field = series_config.get("yField")
                
                if not x_field or not y_field or x_field not in data.columns or y_field not in data.columns:
                    continue
                
                # 获取数据
                scatter_data = []
                for _, row in data.iterrows():
                    scatter_data.append([row[x_field], row[y_field]])
                
                # 添加系列
                series = {
                    "name": series_config.get("name", ""),
                    "type": "scatter",
                    "data": scatter_data
                }
                
                options["series"].append(series)
                options["legend"]["data"].append(series_config.get("name", ""))
        
        elif chart_type == "table":
            # 表格不使用ECharts，直接返回数据
            columns = []
            for column_config in config.get("columns", []):
                field = column_config.get("field")
                if not field or field not in data.columns:
                    continue
                
                columns.append({
                    "field": field,
                    "title": column_config.get("title", field)
                })
            
            # 获取数据
            table_data = data.to_dict(orient="records")
            
            # 设置表格选项
            options = {
                "title": config.get("title", ""),
                "columns": columns,
                "data": table_data
            }
        
        return options
    
    @staticmethod
    def save_chart_config(
        chart_id: str,
        chart_type: str,
        config: Dict[str, Any]
    ) -> str:
        """
        保存图表配置
        
        Args:
            chart_id: 图表ID
            chart_type: 图表类型
            config: 图表配置
            
        Returns:
            str: 配置文件路径
        """
        # 构建配置文件路径
        config_path = os.path.join(CHART_DIR, f"{chart_id}.json")
        
        # 保存配置
        with open(config_path, "w") as f:
            json.dump({
                "id": chart_id,
                "type": chart_type,
                "config": config,
                "created_at": datetime.now().isoformat()
            }, f)
        
        return config_path
    
    @staticmethod
    def load_chart_config(chart_id: str) -> Dict[str, Any]:
        """
        加载图表配置
        
        Args:
            chart_id: 图表ID
            
        Returns:
            Dict[str, Any]: 图表配置
            
        Raises:
            FileNotFoundError: 配置文件不存在
        """
        # 构建配置文件路径
        config_path = os.path.join(CHART_DIR, f"{chart_id}.json")
        
        # 检查文件是否存在
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"图表配置不存在: {chart_id}")
        
        # 加载配置
        with open(config_path, "r") as f:
            return json.load(f)
    
    @staticmethod
    def delete_chart_config(chart_id: str) -> None:
        """
        删除图表配置
        
        Args:
            chart_id: 图表ID
            
        Raises:
            FileNotFoundError: 配置文件不存在
        """
        # 构建配置文件路径
        config_path = os.path.join(CHART_DIR, f"{chart_id}.json")
        
        # 检查文件是否存在
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"图表配置不存在: {chart_id}")
        
        # 删除配置文件
        os.remove(config_path)
    
    @staticmethod
    def list_charts() -> List[Dict[str, Any]]:
        """
        列出所有图表
        
        Returns:
            List[Dict[str, Any]]: 图表列表
        """
        charts = []
        
        # 遍历图表目录
        for file_name in os.listdir(CHART_DIR):
            if file_name.endswith(".json"):
                try:
                    # 加载配置
                    config_path = os.path.join(CHART_DIR, file_name)
                    with open(config_path, "r") as f:
                        config = json.load(f)
                    
                    # 添加到列表
                    charts.append({
                        "id": config.get("id", ""),
                        "type": config.get("type", ""),
                        "title": config.get("config", {}).get("title", ""),
                        "created_at": config.get("created_at", "")
                    })
                except:
                    # 忽略无法加载的配置
                    pass
        
        return charts 