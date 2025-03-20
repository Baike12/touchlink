from typing import Dict, Any, Optional
import pandas as pd
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session

from .celery import celery_app
from .task_logger import get_task_logger
from src.core.services import AnalyticsService, ExportService
from src.core.models import ExportTask
from src.config.database import SessionLocal
from src.utils.logger import setup_logger
from src.utils.exceptions import AnalyticsException, NotFoundException

# 创建日志记录器
logger = setup_logger("export_tasks")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@celery_app.task(bind=True, name="execute_export_task")
def execute_export_task(self, task_id: str) -> Dict[str, Any]:
    """
    执行导出任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 任务结果
    """
    logger.info(f"开始执行导出任务: {task_id}")
    
    # 获取任务日志记录器
    task_logger = get_task_logger(task_id)
    task_logger.info("开始执行导出任务")
    
    # 获取数据库会话
    db = get_db()
    
    try:
        # 获取任务
        task = db.query(ExportTask).filter(ExportTask.id == task_id).first()
        if not task:
            raise NotFoundException(f"导出任务不存在: {task_id}")
        
        # 更新任务状态
        task.status = "running"
        db.commit()
        
        # 更新Celery任务状态
        self.update_state(state="PROGRESS", meta={"status": "running"})
        task_logger.info("任务状态已更新为running")
        
        # 获取配置
        config = task.config
        export_type = task.type
        
        # 如果关联了分析任务，从分析任务获取数据
        if task.analysis_task_id:
            task_logger.info(f"从分析任务获取数据: {task.analysis_task_id}")
            
            # 获取分析任务
            analysis_task = AnalyticsService.get_task(db, task.analysis_task_id)
            
            # 检查分析任务状态
            if analysis_task.status != "completed":
                raise AnalyticsException(f"分析任务未完成: {analysis_task.status}")
            
            # 检查分析任务结果路径
            if not analysis_task.result_path:
                raise AnalyticsException("分析任务没有结果")
            
            # 加载分析任务结果
            result_path = analysis_task.result_path
            index_path = os.path.join(result_path, "index.json")
            
            if not os.path.exists(index_path):
                raise AnalyticsException(f"分析任务结果索引不存在: {index_path}")
            
            # 读取结果索引
            with open(index_path, "r") as f:
                result_index = json.load(f)
            
            # 加载数据
            dataframes = {}
            for name, file_path in result_index.get("files", {}).items():
                if os.path.exists(file_path):
                    dataframes[name] = pd.read_csv(file_path)
            
            if not dataframes:
                raise AnalyticsException("分析任务结果为空")
            
            task_logger.info(f"加载了{len(dataframes)}个数据集")
            
            # 导出数据
            if len(dataframes) == 1:
                # 单个数据集
                df = list(dataframes.values())[0]
                result_path = ExportService.export_dataframe(
                    df=df,
                    format=export_type,
                    filename=task.name,
                    **config.get("options", {})
                )
            else:
                # 多个数据集
                result_path = ExportService.export_multiple_dataframes(
                    dataframes=dataframes,
                    format=export_type,
                    filename=task.name,
                    **config.get("options", {})
                )
        
        # 否则，从配置中获取数据
        else:
            task_logger.info("从配置中获取数据")
            
            # 获取数据
            data = config.get("data", {})
            
            if not data:
                raise AnalyticsException("配置中没有数据")
            
            # 转换为DataFrame
            if isinstance(data, list):
                # 列表数据
                df = pd.DataFrame(data)
                result_path = ExportService.export_dataframe(
                    df=df,
                    format=export_type,
                    filename=task.name,
                    **config.get("options", {})
                )
            elif isinstance(data, dict):
                # 字典数据，可能是多个DataFrame
                dataframes = {}
                for name, sheet_data in data.items():
                    dataframes[name] = pd.DataFrame(sheet_data)
                
                result_path = ExportService.export_multiple_dataframes(
                    dataframes=dataframes,
                    format=export_type,
                    filename=task.name,
                    **config.get("options", {})
                )
            else:
                raise AnalyticsException(f"不支持的数据类型: {type(data)}")
        
        # 更新任务状态
        task.status = "completed"
        task.result_path = result_path
        db.commit()
        
        task_logger.info(f"导出成功: {result_path}")
        logger.info(f"导出任务执行成功: {task_id}")
        
        return {
            "status": "completed",
            "task_id": task_id,
            "result_path": result_path
        }
    
    except Exception as e:
        # 更新任务状态
        try:
            task = db.query(ExportTask).filter(ExportTask.id == task_id).first()
            if task:
                task.status = "failed"
                db.commit()
            task_logger.error(f"任务执行失败: {str(e)}")
        except:
            task_logger.error(f"更新任务状态失败: {str(e)}")
        
        logger.error(f"导出任务执行失败: {str(e)}")
        
        # 重新抛出异常，让Celery处理
        raise 