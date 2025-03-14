import os
from dotenv import load_dotenv
import urllib.parse

# 加载环境变量
load_dotenv()

# 应用设置
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 数据库设置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "touchlink")
USER_DB_NAME = os.getenv("USER_DB_NAME", "user_database")

# Redis设置
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# Celery设置
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# 安全设置
SECRET_KEY = os.getenv("SECRET_KEY", "touchlink_development_secret_key")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# CORS设置
CORS_ORIGINS = eval(os.getenv("CORS_ORIGINS", '["http://localhost:5173"]'))

# 文件存储设置
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "104857600"))  # 默认100MB

# 数据库URL
def get_database_url():
    """获取数据库URL"""
    # 处理密码中的特殊字符
    password = urllib.parse.quote_plus(DB_PASSWORD)
    return f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 用户数据库URL
def get_user_database_url():
    """获取用户数据库URL"""
    # 处理密码中的特殊字符
    password = urllib.parse.quote_plus(DB_PASSWORD)
    return f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{USER_DB_NAME}"

# 设置对象
class Settings:
    DEBUG = DEBUG
    DB_HOST = DB_HOST
    DB_PORT = DB_PORT
    DB_USER = DB_USER
    DB_PASSWORD = DB_PASSWORD
    DB_NAME = DB_NAME
    USER_DB_NAME = USER_DB_NAME
    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_DB = REDIS_DB
    REDIS_PASSWORD = REDIS_PASSWORD
    CELERY_BROKER_URL = CELERY_BROKER_URL
    CELERY_RESULT_BACKEND = CELERY_RESULT_BACKEND
    SECRET_KEY = SECRET_KEY
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    CORS_ORIGINS = CORS_ORIGINS
    UPLOAD_DIR = UPLOAD_DIR
    MAX_UPLOAD_SIZE = MAX_UPLOAD_SIZE

# 创建设置实例
settings = Settings() 