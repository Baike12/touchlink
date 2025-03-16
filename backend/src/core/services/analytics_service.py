from typing import Dict, Any, List, Optional
import pandas as pd
import uuid
from sqlalchemy.orm import Session

from backend.src.core.analytics import Pipeline, OperatorFactory
from backend.src.core.services import DataSourceService
from backend.src.core.models import AnalysisTask
from backend.src.utils.exceptions import AnalyticsException, NotFoundException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("analytics_service")


class AnalyticsService:
    """分析引擎服务"""
    
    @staticmethod
    def get_available_operators() -> Dict[str, Dict[str, Any]]:
        """
        获取可用的操作类型
        
        Returns:
            Dict[str, Dict[str, Any]]: 操作类型信息
        """
        return OperatorFactory.get_all_operator_info()
    
    @staticmethod
    def create_pipeline(name: str, description: str = None) -> Pipeline:
        """
        创建分析流水线
        
        Args:
            name: 流水线名称
            description: 流水线描述
            
        Returns:
            Pipeline: 分析流水线
        """
        return Pipeline(name=name, description=description)
    
    @staticmethod
    def load_pipeline(pipeline_data: Dict[str, Any]) -> Pipeline:
        """
        加载分析流水线
        
        Args:
            pipeline_data: 流水线数据
            
        Returns:
            Pipeline: 分析流水线
        """
        return Pipeline.from_dict(pipeline_data)
    
    @staticmethod
    def create_task(
        db: Session,
        user_id: str,
        name: str,
        pipeline: Pipeline,
        datasource_id: Optional[str] = None
    ) -> AnalysisTask:
        """
        创建分析任务
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            name: 任务名称
            pipeline: 分析流水线
            datasource_id: 数据源ID
            
        Returns:
            AnalysisTask: 分析任务
        """
        # 创建任务
        task = AnalysisTask(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            pipeline=pipeline.to_dict(),
            status="pending",
            datasource_id=datasource_id
        )
        
        # 保存到数据库
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"创建分析任务: {task.id}, 名称: {task.name}")
        return task
    
    @staticmethod
    def get_task(db: Session, task_id: str) -> AnalysisTask:
        """
        获取分析任务
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Returns:
            AnalysisTask: 分析任务
            
        Raises:
            NotFoundException: 任务不存在
        """
        task = db.query(AnalysisTask).filter(AnalysisTask.id == task_id).first()
        if not task:
            raise NotFoundException(f"分析任务不存在: {task_id}")
        
        return task
    
    @staticmethod
    def get_user_tasks(db: Session, user_id: str) -> List[AnalysisTask]:
        """
        获取用户的所有分析任务
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            List[AnalysisTask]: 分析任务列表
        """
        return db.query(AnalysisTask).filter(AnalysisTask.user_id == user_id).all()
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: str,
        name: Optional[str] = None,
        pipeline: Optional[Pipeline] = None,
        status: Optional[str] = None,
        result_path: Optional[str] = None
    ) -> AnalysisTask:
        """
        更新分析任务
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            name: 任务名称
            pipeline: 分析流水线
            status: 任务状态
            result_path: 结果路径
            
        Returns:
            AnalysisTask: 分析任务
            
        Raises:
            NotFoundException: 任务不存在
        """
        # 获取任务
        task = AnalyticsService.get_task(db, task_id)
        
        # 更新任务
        if name:
            task.name = name
        
        if pipeline:
            task.pipeline = pipeline.to_dict()
        
        if status:
            task.status = status
        
        if result_path:
            task.result_path = result_path
        
        # 保存到数据库
        db.commit()
        db.refresh(task)
        
        logger.info(f"更新分析任务: {task.id}")
        return task
    
    @staticmethod
    def delete_task(db: Session, task_id: str) -> None:
        """
        删除分析任务
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Raises:
            NotFoundException: 任务不存在
        """
        # 获取任务
        task = AnalyticsService.get_task(db, task_id)
        
        # 删除任务
        db.delete(task)
        db.commit()
        
        logger.info(f"删除分析任务: {task_id}")
    
    @staticmethod
    def execute_pipeline(
        db: Session,
        pipeline: Pipeline,
        datasource_id: Optional[str] = None,
        initial_data: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        执行分析流水线
        
        Args:
            db: 数据库会话
            pipeline: 分析流水线
            datasource_id: 数据源ID
            initial_data: 初始数据
            
        Returns:
            Dict[str, pd.DataFrame]: 执行结果
            
        Raises:
            AnalyticsException: 执行失败
        """
        # 初始化数据
        data = initial_data or {}
        
        # 如果指定了数据源，从数据源加载数据
        if datasource_id:
            try:
                # 连接数据源
                source = DataSourceService.connect_datasource(datasource_id, db)
                
                # 获取表列表
                tables = source.get_tables()
                
                # 加载数据
                for table in tables:
                    df = source.get_sample_data(table)
                    data[table] = df
                    
                    logger.info(f"从数据源加载表: {table}, 行数: {len(df)}")
            
            except Exception as e:
                logger.error(f"从数据源加载数据失败: {str(e)}")
                raise AnalyticsException(f"从数据源加载数据失败: {str(e)}")
        
        # 执行流水线
        try:
            result = pipeline.execute(data)
            logger.info(f"流水线执行成功，生成数据集: {', '.join(result.keys())}")
            return result
        
        except Exception as e:
            logger.error(f"流水线执行失败: {str(e)}")
            raise AnalyticsException(f"流水线执行失败: {str(e)}")
    
    @staticmethod
    def execute_task(db: Session, task_id: str) -> Dict[str, pd.DataFrame]:
        """
        执行分析任务
        
        Args:
            db: 数据库会话
            task_id: 任务ID
            
        Returns:
            Dict[str, pd.DataFrame]: 执行结果
            
        Raises:
            NotFoundException: 任务不存在
            AnalyticsException: 执行失败
        """
        # 获取任务
        task = AnalyticsService.get_task(db, task_id)
        
        # 更新任务状态
        task.status = "running"
        db.commit()
        
        try:
            # 加载流水线
            pipeline = Pipeline.from_dict(task.pipeline)
            
            # 执行流水线
            result = AnalyticsService.execute_pipeline(db, pipeline, task.datasource_id)
            
            # 更新任务状态
            task.status = "completed"
            db.commit()
            
            logger.info(f"分析任务执行成功: {task.id}")
            return result
        
        except Exception as e:
            # 更新任务状态
            task.status = "failed"
            db.commit()
            
            logger.error(f"分析任务执行失败: {str(e)}")
            raise AnalyticsException(f"分析任务执行失败: {str(e)}") 