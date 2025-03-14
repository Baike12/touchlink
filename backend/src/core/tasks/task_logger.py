import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 配置日志目录
LOG_DIR = os.path.join("logs", "tasks")
os.makedirs(LOG_DIR, exist_ok=True)


class TaskLogger:
    """任务日志记录器"""
    
    def __init__(self, task_id: str):
        """
        初始化任务日志记录器
        
        Args:
            task_id: 任务ID
        """
        self.task_id = task_id
        self.log_file = os.path.join(LOG_DIR, f"{task_id}.log")
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        Returns:
            logging.Logger: 日志记录器
        """
        # 创建日志记录器
        logger = logging.getLogger(f"task_{self.task_id}")
        logger.setLevel(logging.INFO)
        
        # 清除已有的处理器
        if logger.handlers:
            logger.handlers.clear()
        
        # 创建文件处理器
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        记录信息日志
        
        Args:
            message: 日志消息
            data: 附加数据
        """
        self._log(logging.INFO, message, data)
    
    def warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        记录警告日志
        
        Args:
            message: 日志消息
            data: 附加数据
        """
        self._log(logging.WARNING, message, data)
    
    def error(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        记录错误日志
        
        Args:
            message: 日志消息
            data: 附加数据
        """
        self._log(logging.ERROR, message, data)
    
    def _log(self, level: int, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            data: 附加数据
        """
        # 构建日志消息
        log_message = message
        
        # 如果有附加数据，添加到日志消息中
        if data:
            try:
                log_message += f" - {json.dumps(data)}"
            except:
                log_message += f" - {str(data)}"
        
        # 记录日志
        self.logger.log(level, log_message)
    
    def get_logs(self, max_lines: int = 100) -> str:
        """
        获取日志内容
        
        Args:
            max_lines: 最大行数
            
        Returns:
            str: 日志内容
        """
        if not os.path.exists(self.log_file):
            return ""
        
        with open(self.log_file, "r") as f:
            lines = f.readlines()
        
        # 返回最后max_lines行
        return "".join(lines[-max_lines:])


def get_task_logger(task_id: str) -> TaskLogger:
    """
    获取任务日志记录器
    
    Args:
        task_id: 任务ID
        
    Returns:
        TaskLogger: 任务日志记录器
    """
    return TaskLogger(task_id) 