from typing import Dict, Any, List, Optional
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.core.models import Dashboard, DashboardItem, Chart, User
from src.core.services import VisualizationService
from src.utils.logger import setup_logger
from src.utils.exceptions import (
    ResourceNotFoundException,
    ValidationException,
    DatabaseException
)

# 创建日志记录器
logger = setup_logger("dashboard_service")


class DashboardService:
    """仪表盘服务"""
    
    def __init__(self, db: Session):
        """
        初始化仪表盘服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.visualization_service = VisualizationService(db)
    
    def create_dashboard(
        self,
        title: str,
        description: Optional[str] = None,
        layout: Optional[Dict[str, Any]] = None
    ) -> Dashboard:
        """
        创建仪表盘
        
        Args:
            title: 仪表盘标题
            description: 仪表盘描述
            layout: 仪表盘布局
            
        Returns:
            Dashboard: 创建的仪表盘
            
        Raises:
            ValidationException: 验证失败
            DatabaseException: 数据库错误
        """
        try:
            # 创建仪表盘
            dashboard = Dashboard(
                title=title,
                description=description,
                layout=json.dumps(layout) if layout else None
            )
            
            # 保存到数据库
            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)
            
            return dashboard
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"创建仪表盘时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("创建仪表盘时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"创建仪表盘时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def get_dashboard(self, dashboard_id: str) -> Dashboard:
        """
        获取仪表盘
        
        Args:
            dashboard_id: 仪表盘ID
            
        Returns:
            Dashboard: 仪表盘
            
        Raises:
            ResourceNotFoundException: 资源不存在
        """
        dashboard = self.db.query(Dashboard).filter(
            Dashboard.id == dashboard_id
        ).first()
        
        if not dashboard:
            raise ResourceNotFoundException(f"仪表盘不存在: {dashboard_id}")
        
        return dashboard
    
    def get_dashboards(self) -> List[Dashboard]:
        """
        获取仪表盘列表
        
        Returns:
            List[Dashboard]: 仪表盘列表
        """
        return self.db.query(Dashboard).all()
    
    def update_dashboard(
        self,
        dashboard_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        layout: Optional[Dict[str, Any]] = None
    ) -> Dashboard:
        """
        更新仪表盘
        
        Args:
            dashboard_id: 仪表盘ID
            title: 仪表盘标题
            description: 仪表盘描述
            layout: 仪表盘布局
            
        Returns:
            Dashboard: 更新后的仪表盘
            
        Raises:
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取仪表盘
            dashboard = self.get_dashboard(dashboard_id)
            
            # 更新字段
            if title:
                dashboard.title = title
            
            if description is not None:
                dashboard.description = description
            
            if layout is not None:
                dashboard.layout = json.dumps(layout)
            
            # 保存到数据库
            self.db.commit()
            self.db.refresh(dashboard)
            
            return dashboard
        
        except ResourceNotFoundException as e:
            # 回滚事务
            self.db.rollback()
            # 重新抛出异常
            raise e
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新仪表盘时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("更新仪表盘时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新仪表盘时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def delete_dashboard(self, dashboard_id: str) -> None:
        """
        删除仪表盘
        
        Args:
            dashboard_id: 仪表盘ID
            
        Raises:
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取仪表盘
            dashboard = self.get_dashboard(dashboard_id)
            
            # 从数据库中删除
            self.db.delete(dashboard)
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
            logger.error(f"删除仪表盘时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("删除仪表盘时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"删除仪表盘时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def add_chart_to_dashboard(
        self,
        dashboard_id: str,
        chart_id: str,
        position_x: int = 0,
        position_y: int = 0,
        width: int = 4,
        height: int = 4,
        config: Optional[Dict[str, Any]] = None
    ) -> DashboardItem:
        """
        添加图表到仪表盘
        
        Args:
            dashboard_id: 仪表盘ID
            chart_id: 图表ID
            position_x: X坐标
            position_y: Y坐标
            width: 宽度
            height: 高度
            config: 配置
            
        Returns:
            DashboardItem: 仪表盘项目
            
        Raises:
            ResourceNotFoundException: 资源不存在
            ValidationException: 验证失败
            DatabaseException: 数据库错误
        """
        try:
            # 获取仪表盘
            dashboard = self.get_dashboard(dashboard_id)
            
            # 验证图表
            chart = self.visualization_service.get_chart(chart_id)
            
            # 创建仪表盘项目
            dashboard_item = DashboardItem(
                dashboard_id=dashboard_id,
                chart_id=chart_id,
                position_x=position_x,
                position_y=position_y,
                width=width,
                height=height,
                config=json.dumps(config) if config else None
            )
            
            # 保存到数据库
            self.db.add(dashboard_item)
            self.db.commit()
            self.db.refresh(dashboard_item)
            
            return dashboard_item
        
        except ResourceNotFoundException as e:
            # 回滚事务
            self.db.rollback()
            # 重新抛出异常
            raise e
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"添加图表到仪表盘时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("添加图表到仪表盘时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"添加图表到仪表盘时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def update_dashboard_item(
        self,
        item_id: str,
        position_x: Optional[int] = None,
        position_y: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> DashboardItem:
        """
        更新仪表盘项目
        
        Args:
            item_id: 项目ID
            position_x: X坐标
            position_y: Y坐标
            width: 宽度
            height: 高度
            config: 配置
            
        Returns:
            DashboardItem: 更新后的仪表盘项目
            
        Raises:
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取仪表盘项目
            dashboard_item = self.db.query(DashboardItem).filter(
                DashboardItem.id == item_id
            ).first()
            
            if not dashboard_item:
                raise ResourceNotFoundException(f"仪表盘项目不存在: {item_id}")
            
            # 更新字段
            if position_x is not None:
                dashboard_item.position_x = position_x
            
            if position_y is not None:
                dashboard_item.position_y = position_y
            
            if width is not None:
                dashboard_item.width = width
            
            if height is not None:
                dashboard_item.height = height
            
            if config is not None:
                dashboard_item.config = json.dumps(config)
            
            # 保存到数据库
            self.db.commit()
            self.db.refresh(dashboard_item)
            
            return dashboard_item
        
        except ResourceNotFoundException as e:
            # 回滚事务
            self.db.rollback()
            # 重新抛出异常
            raise e
        
        except SQLAlchemyError as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新仪表盘项目时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("更新仪表盘项目时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"更新仪表盘项目时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def remove_chart_from_dashboard(self, item_id: str) -> None:
        """
        从仪表盘中移除图表
        
        Args:
            item_id: 项目ID
            
        Raises:
            ResourceNotFoundException: 资源不存在
            DatabaseException: 数据库错误
        """
        try:
            # 获取仪表盘项目
            dashboard_item = self.db.query(DashboardItem).filter(
                DashboardItem.id == item_id
            ).first()
            
            if not dashboard_item:
                raise ResourceNotFoundException(f"仪表盘项目不存在: {item_id}")
            
            # 从数据库中删除
            self.db.delete(dashboard_item)
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
            logger.error(f"从仪表盘中移除图表时发生数据库错误: {str(e)}")
            # 抛出异常
            raise DatabaseException("从仪表盘中移除图表时发生数据库错误")
        
        except Exception as e:
            # 回滚事务
            self.db.rollback()
            # 记录错误
            logger.error(f"从仪表盘中移除图表时发生错误: {str(e)}")
            # 抛出异常
            raise e
    
    def get_dashboard_with_items(self, dashboard_id: str) -> Dict[str, Any]:
        """
        获取仪表盘及其项目
        
        Args:
            dashboard_id: 仪表盘ID
            
        Returns:
            Dict[str, Any]: 仪表盘及其项目
            
        Raises:
            ResourceNotFoundException: 资源不存在
        """
        # 获取仪表盘
        dashboard = self.get_dashboard(dashboard_id)
        
        # 获取仪表盘项目
        dashboard_items = self.db.query(DashboardItem).filter(
            DashboardItem.dashboard_id == dashboard_id
        ).all()
        
        # 构建响应
        result = {
            "id": dashboard.id,
            "title": dashboard.title,
            "description": dashboard.description,
            "layout": json.loads(dashboard.layout) if dashboard.layout else None,
            "created_at": dashboard.created_at,
            "updated_at": dashboard.updated_at,
            "items": []
        }
        
        # 添加项目
        for item in dashboard_items:
            # 获取图表
            chart = self.db.query(Chart).filter(Chart.id == item.chart_id).first()
            
            if chart:
                result["items"].append({
                    "id": item.id,
                    "chart": {
                        "id": chart.id,
                        "title": chart.title,
                        "type": chart.type,
                        "config": json.loads(chart.config)
                    },
                    "position_x": item.position_x,
                    "position_y": item.position_y,
                    "width": item.width,
                    "height": item.height,
                    "config": json.loads(item.config) if item.config else None
                })
        
        return result 