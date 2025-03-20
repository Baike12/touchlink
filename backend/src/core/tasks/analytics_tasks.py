from typing import Dict, Any, Optional
import pandas as pd
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session

from .celery import celery_app
from .task_logger import get_task_logger
from src.core.services import AnalyticsService, DataSourceService
from src.core.analytics import Pipeline
from src.config.database import SessionLocal
from src.utils.logger import setup_logger
from src.utils.exceptions import AnalyticsException, NotFoundException

# 创建日志记录器
logger = setup_logger("analytics_tasks")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@celery_app.task(bind=True, name="execute_analysis_task")
def execute_analysis_task(self, task_id: str) -> Dict[str, Any]:
    """
    执行分析任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 任务结果
    """
    logger.info(f"开始执行分析任务: {task_id}")
    
    # 获取任务日志记录器
    task_logger = get_task_logger(task_id)
    task_logger.info("开始执行分析任务")
    
    # 获取数据库会话
    db = get_db()
    
    try:
        # 更新任务状态
        task = AnalyticsService.get_task(db, task_id)
        task.status = "running"
        db.commit()
        
        # 更新Celery任务状态
        self.update_state(state="PROGRESS", meta={"status": "running"})
        task_logger.info("任务状态已更新为running")
        
        # 加载流水线
        pipeline = Pipeline.from_dict(task.pipeline)
        task_logger.info(f"加载流水线: {pipeline.name}, 步骤数: {len(pipeline.steps)}")
        
        # 执行流水线
        task_logger.info("开始执行流水线")
        result = AnalyticsService.execute_pipeline(db, pipeline, task.datasource_id)
        task_logger.info(f"流水线执行完成，生成数据集: {', '.join(result.keys())}")
        
        # 保存结果
        task_logger.info("开始保存结果")
        result_path = save_result(result, task_id)
        task_logger.info(f"结果已保存到: {result_path}")
        
        # 更新任务状态
        task.status = "completed"
        task.result_path = result_path
        db.commit()
        task_logger.info("任务状态已更新为completed")
        
        logger.info(f"分析任务执行成功: {task_id}")
        task_logger.info("分析任务执行成功")
        
        return {
            "status": "completed",
            "task_id": task_id,
            "result_path": result_path
        }
    
    except Exception as e:
        # 更新任务状态
        try:
            task = AnalyticsService.get_task(db, task_id)
            task.status = "failed"
            db.commit()
            task_logger.error(f"任务执行失败: {str(e)}")
        except:
            task_logger.error(f"更新任务状态失败: {str(e)}")
        
        logger.error(f"分析任务执行失败: {str(e)}")
        
        # 重新抛出异常，让Celery处理
        raise AnalyticsException(f"分析任务执行失败: {str(e)}")


@celery_app.task(bind=True, name="cancel_analysis_task")
def cancel_analysis_task(self, task_id: str) -> Dict[str, Any]:
    """
    取消分析任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        Dict[str, Any]: 取消结果
    """
    logger.info(f"取消分析任务: {task_id}")
    
    # 获取任务日志记录器
    task_logger = get_task_logger(task_id)
    task_logger.info("开始取消分析任务")
    
    # 获取数据库会话
    db = get_db()
    
    try:
        # 更新任务状态
        task = AnalyticsService.get_task(db, task_id)
        
        # 如果任务已经完成或失败，无法取消
        if task.status in ["completed", "failed"]:
            task_logger.warning(f"无法取消已{task.status}的任务")
            return {
                "status": "error",
                "message": f"无法取消已{task.status}的任务"
            }
        
        # 更新任务状态
        task.status = "canceled"
        db.commit()
        task_logger.info("任务状态已更新为canceled")
        
        # 撤销Celery任务
        celery_app.control.revoke(task_id, terminate=True)
        task_logger.info("Celery任务已撤销")
        
        logger.info(f"分析任务已取消: {task_id}")
        task_logger.info("分析任务已取消")
        
        return {
            "status": "canceled",
            "task_id": task_id
        }
    
    except Exception as e:
        logger.error(f"取消分析任务失败: {str(e)}")
        task_logger.error(f"取消分析任务失败: {str(e)}")
        raise AnalyticsException(f"取消分析任务失败: {str(e)}")


def save_result(result: Dict[str, pd.DataFrame], task_id: str) -> str:
    """
    保存分析结果
    
    Args:
        result: 分析结果
        task_id: 任务ID
        
    Returns:
        str: 结果路径
    """
    # 创建结果目录
    result_dir = os.path.join("results", task_id)
    os.makedirs(result_dir, exist_ok=True)
    
    # 保存结果
    result_files = {}
    for name, df in result.items():
        # 保存为CSV
        file_path = os.path.join(result_dir, f"{name}.csv")
        df.to_csv(file_path, index=False)
        result_files[name] = file_path
    
    # 保存结果索引
    index_path = os.path.join(result_dir, "index.json")
    with open(index_path, "w") as f:
        json.dump({
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "files": result_files
        }, f)
    
    return result_dir 