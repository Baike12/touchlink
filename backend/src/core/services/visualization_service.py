from typing import Dict, Any, List, Optional
import json
import pandas as pd
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.core.models import Chart, User, AnalysisTask
from src.core.visualization.chart_service import ChartService
from src.utils.logger import setup_logger
from src.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)

# 创建日志记录器
logger = setup_logger("visualization_service")


class VisualizationService:
    """可视化服务"""
    
    def __init__(self, db: Session):
        """
        初始化可视化服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.chart_service = ChartService()
    
    def create_chart(
        self,
        title: str,
        chart_type: str,
        config: Dict[str, Any],
        description: Optional[str] = None,
        analysis_task_id: Optional[str] = None,
        data_source: Optional[Dict[str, Any]] = None,
        tables: Optional[List[str]] = None
    ) -> Chart:
        """
        创建图表（只保存元数据，不处理实际数据）
        
        Args:
            title: 图表标题
            chart_type: 图表类型
            config: 图表配置（元数据）
            description: 图表描述
            analysis_task_id: 分析任务ID
            data_source: 数据源配置
            tables: 相关表列表
            
        Returns:
            Chart: 创建的图表
            
        Raises:
            ValidationException: 验证失败
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 验证图表类型
            if chart_type not in self.chart_service.CHART_TYPES:
                logger.error(f"不支持的图表类型: {chart_type}")
                raise ValidationException(f"不支持的图表类型: {chart_type}")
            
            # 记录详细的配置信息
            logger.info(f"创建图表: 类型={chart_type}, 标题={title}")
            logger.debug(f"图表配置: {json.dumps(config)}")
            
            # 创建图表（只保存元数据）
            chart = Chart(
                title=title,
                description=description,
                type=chart_type,
                config=json.dumps(config),
                analysis_task_id=analysis_task_id,
                data_source=json.dumps(data_source) if data_source else None
            )
            
            # 保存到数据库
            self.db.add(chart)
            self.db.commit()
            self.db.refresh(chart)
            
            # 保存图表配置（包括表信息）
            chart_config = {
                "id": chart.id,
                "type": chart_type,
                "config": config,
                "tables": tables
            }
            self.chart_service.save_chart_config(
                chart_id=chart.id,
                chart_type=chart_type,
                config=chart_config
            )
            
            logger.info(f"图表创建成功: {chart.id}")
            return chart
        
        except ValidationException as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"创建图表验证失败: {str(e)}")
            # 重新抛出异常
            raise e
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"创建图表时发生数据库错误: {str(e)}")
            logger.exception("创建图表详细错误:")
            # 抛出异常
            raise DatabaseException(f"创建图表时发生数据库错误: {str(e)}")
    
    def load_chart_data(
        self,
        chart_id: str
    ) -> Dict[str, Any]:
        """
        加载图表数据（从数据源获取实际数据）
        
        Args:
            chart_id: 图表ID
            
        Returns:
            Dict[str, Any]: 图表数据和选项
            
        Raises:
            ResourceNotFoundException: 资源不存在
            ValidationException: 验证失败
            DatabaseException: 数据库错误
        """
        try:
            # 获取图表
            chart = self.get_chart(chart_id)
            
            # 解析配置
            chart_type = chart.type
            config = json.loads(chart.config) if isinstance(chart.config, str) else chart.config
            
            # 获取数据源信息
            data_source = None
            if chart.data_source:
                data_source = json.loads(chart.data_source) if isinstance(chart.data_source, str) else chart.data_source
            
            # 加载图表配置（包括表信息）
            try:
                chart_config = self.chart_service.load_chart_config(chart_id)
                tables = chart_config.get("tables", [])
            except FileNotFoundError:
                tables = []
            
            logger.info(f"加载图表数据: {chart_id}, 类型={chart_type}")
            logger.debug(f"图表配置: {json.dumps(config)}")
            
            # 生成模拟数据
            data = self.generate_mock_data(chart_type, config)
            
            # 生成图表选项
            options = {
                "id": chart.id,
                "title": chart.title,
                "description": chart.description,
                "type": chart_type,
                "config": config,
                "data_source": data_source,
                "tables": tables,
                "data": data
            }
            
            return options
        
        except (ResourceNotFoundException, ValidationException) as e:
            # 记录错误
            logger.error(f"加载图表数据失败: {str(e)}")
            # 重新抛出异常
            raise e
        
        except Exception as e:
            # 记录错误
            logger.error(f"加载图表数据时发生错误: {str(e)}")
            logger.exception("加载图表数据详细错误:")
            # 抛出异常
            raise DatabaseException(f"加载图表数据时发生错误: {str(e)}")
    
    def generate_mock_data(self, chart_type: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成模拟数据
        
        Args:
            chart_type: 图表类型
            config: 图表配置
            
        Returns:
            List[Dict[str, Any]]: 模拟数据
        """
        import random
        
        # 根据图表类型生成不同的模拟数据
        if chart_type in ["bar", "line", "area"]:
            # 获取X轴字段
            x_field = config.get("xAxis", {}).get("field", "category")
            
            # 获取系列字段
            series = config.get("series", [])
            if not series:
                series = [{"name": "系列1", "field": "value"}]
            
            # 生成类别数据
            categories = ["类别1", "类别2", "类别3", "类别4", "类别5", "类别6", "类别7"]
            
            # 生成数据
            data = []
            for i, category in enumerate(categories):
                item = {x_field: category}
                for serie in series:
                    field = serie.get("field", serie.get("name", "value"))
                    item[field] = random.randint(10, 100)
                data.append(item)
            
            return data
        
        elif chart_type == "pie":
            # 获取名称字段和值字段
            name_field = config.get("nameField", "name")
            value_field = config.get("valueField", "value")
            
            # 生成数据
            data = []
            categories = ["类别1", "类别2", "类别3", "类别4", "类别5"]
            for category in categories:
                data.append({
                    name_field: category,
                    value_field: random.randint(10, 100)
                })
            
            return data
        
        elif chart_type == "scatter":
            # 获取X轴和Y轴字段
            x_field = config.get("xAxis", {}).get("field", "x")
            y_field = config.get("yAxis", {}).get("field", "y")
            
            # 生成数据
            data = []
            for i in range(20):
                data.append({
                    x_field: random.randint(10, 100),
                    y_field: random.randint(10, 100)
                })
            
            return data
        
        elif chart_type == "table":
            # 获取列定义
            columns = config.get("columns", [])
            if not columns:
                columns = [
                    {"title": "名称", "dataIndex": "name"},
                    {"title": "值", "dataIndex": "value"}
                ]
            
            # 生成数据
            data = []
            for i in range(10):
                item = {}
                for column in columns:
                    data_index = column.get("dataIndex", "")
                    if data_index:
                        item[data_index] = f"数据{i+1}-{data_index}"
                data.append(item)
            
            return data
        
        else:
            # 默认返回空数据
            return []
    
    def get_chart(self, chart_id: str) -> Chart:
        """
        获取图表
        
        Args:
            chart_id: 图表ID
            
        Returns:
            Chart: 图表
            
        Raises:
            ResourceNotFoundException: 资源不存在
        """
        chart = self.db.query(Chart).filter(
            Chart.id == chart_id
        ).first()
        
        if not chart:
            raise ResourceNotFoundException(f"图表不存在: {chart_id}")
        
        return chart
    
    def get_charts(self, analysis_task_id: Optional[str] = None) -> List[Chart]:
        """
        获取图表列表
        
        Args:
            analysis_task_id: 分析任务ID
            
        Returns:
            List[Chart]: 图表列表
        """
        query = self.db.query(Chart)
        
        if analysis_task_id:
            query = query.filter(Chart.analysis_task_id == analysis_task_id)
        
        return query.all()
    
    def update_chart(
        self,
        chart_id: str,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        chart_type: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        data_source: Optional[Dict[str, Any]] = None
    ) -> Chart:
        """
        更新图表
        
        Args:
            chart_id: 图表ID
            user_id: 用户ID
            title: 图表标题
            description: 图表描述
            chart_type: 图表类型
            config: 图表配置
            data_source: 数据源配置
            
        Returns:
            Chart: 更新后的图表
            
        Raises:
            ValidationException: 验证失败
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取图表
            chart = self.get_chart(chart_id)
            
            # 更新图表类型和配置
            if chart_type and config:
                # 验证图表配置
                if not self.chart_service.validate_chart_config(chart_type, config):
                    raise ValidationException("图表配置无效")
                
                chart.type = chart_type
                chart.config = json.dumps(config)
                
                # 保存图表配置
                self.chart_service.save_chart_config(
                    chart_id=chart.id,
                    chart_type=chart_type,
                    config=config
                )
            
            # 更新其他字段
            if title:
                chart.title = title
            
            if description is not None:
                chart.description = description
            
            if data_source is not None:
                chart.data_source = json.dumps(data_source)
            
            # 保存到数据库
            self.db.commit()
            self.db.refresh(chart)
            
            return chart
        
        except (ValidationException, ResourceNotFoundException) as e:
            # 回滚事务
            self.db.rollback()
            # 重新抛出异常
            raise e
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新图表时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("更新图表时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新图表时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def delete_chart(self, chart_id: str, user_id: str) -> None:
        """
        删除图表
        
        Args:
            chart_id: 图表ID
            user_id: 用户ID
            
        Raises:
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取图表
            chart = self.get_chart(chart_id)
            
            # 删除图表配置
            try:
                self.chart_service.delete_chart_config(chart_id)
            except FileNotFoundError:
                # 忽略文件不存在的错误
                pass
            
            # 从数据库中删除
            self.db.delete(chart)
            self.db.commit()
        
        except ResourceNotFoundException as e:
            # 回滚事务
            self.db.rollback()
            # 重新抛出异常
            raise e
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"删除图表时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("删除图表时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"删除图表时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def generate_chart_options(
        self,
        chart_id: str,
        user_id: str,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        生成图表选项
        
        Args:
            chart_id: 图表ID
            user_id: 用户ID
            data: 数据
            
        Returns:
            Dict[str, Any]: 图表选项
            
        Raises:
            ResourceNotFoundException: 资源不存在
            ValidationException: 验证失败
        """
        # 获取图表
        chart = self.get_chart(chart_id)
        
        # 解析配置
        chart_type = chart.type
        config = json.loads(chart.config)
        
        # 如果没有提供数据，尝试从分析任务获取
        if data is None and chart.analysis_task_id:
            # 获取分析任务
            analysis_task = self.db.query(AnalysisTask).filter(
                AnalysisTask.id == chart.analysis_task_id
            ).first()
            
            if not analysis_task or not analysis_task.result_path:
                raise ValidationException("无法获取分析任务数据")
            
            # 加载数据
            try:
                data = pd.read_csv(analysis_task.result_path)
            except Exception as e:
                logger.error(f"加载分析任务数据时发生错误: {str(e)}")
                raise ValidationException("无法加载分析任务数据")
        
        # 如果仍然没有数据，尝试从数据源配置获取
        if data is None and chart.data_source:
            data_source = json.loads(chart.data_source)
            
            # TODO: 根据数据源配置加载数据
            # 这里需要实现从数据源配置加载数据的逻辑
            
            if data is None:
                raise ValidationException("无法从数据源获取数据")
        
        # 如果没有数据，抛出异常
        if data is None:
            raise ValidationException("未提供数据")
        
        # 生成图表选项
        try:
            options = self.chart_service.generate_chart_options(
                chart_type=chart_type,
                data=data,
                config=config
            )
            
            return options
        
        except Exception as e:
            logger.error(f"生成图表选项时发生错误: {str(e)}")
            raise ValidationException(f"生成图表选项时发生错误: {str(e)}")
    
    def list_chart_types(self) -> List[str]:
        """
        列出支持的图表类型
        
        Returns:
            List[str]: 图表类型列表
        """
        from src.core.visualization.chart_service import CHART_TYPES
        return CHART_TYPES 