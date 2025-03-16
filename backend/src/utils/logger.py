import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 获取项目根目录
def get_project_root():
    """获取项目根目录"""
    # 当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 向上三级目录即为项目根目录 (backend/src/utils -> backend/src -> backend -> root)
    return os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

# 项目根目录
PROJECT_ROOT = get_project_root()
# 默认日志文件路径
DEFAULT_LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "backend.log")

def setup_logger(
    name: str,
    log_level: str = "info",
    log_file: str = DEFAULT_LOG_FILE,
    log_format: str = DEFAULT_LOG_FORMAT,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_level: 日志级别
        log_file: 日志文件路径
        log_format: 日志格式
        max_file_size: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
        
    Returns:
        logging.Logger: 日志记录器
    """
    # 获取日志级别
    level = LOG_LEVELS.get(log_level.lower(), logging.INFO)
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 创建默认日志记录器
default_logger = setup_logger(
    "touchlink",
    log_level=os.getenv("LOG_LEVEL", "info"),
    log_file=DEFAULT_LOG_FILE
) 