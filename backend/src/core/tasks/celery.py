from celery import Celery
from src.config.settings import settings
from src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("celery_app")

# 创建Celery实例
celery_app = Celery(
    "touchlink",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["core.tasks.analytics_tasks"]
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    task_acks_late=True,  # 任务执行完成后再确认
    task_reject_on_worker_lost=True,  # 工作进程丢失时拒绝任务
)

# 启动Celery
if __name__ == "__main__":
    celery_app.start() 