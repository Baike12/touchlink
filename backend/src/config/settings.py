import os
from dotenv import load_dotenv
import urllib.parse
import sys

# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录的路径（backend目录）
root_dir = os.path.dirname(os.path.dirname(current_dir))
# 构建.env文件的完整路径
env_path = os.path.join(root_dir, '.env')

# 加载环境变量
if not load_dotenv(env_path):
    print(f"错误：无法加载环境变量文件 {env_path}")
    sys.exit(1)

# 检查必要的环境变量
required_env_vars = {
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DB_USER": os.getenv("DB_USER"),
    "DB_PASSWORD": os.getenv("DB_PASSWORD"),
    "DB_NAME": os.getenv("DB_NAME")
}

missing_vars = [var for var, value in required_env_vars.items() if value is None]
if missing_vars:
    print(f"错误：缺少必要的环境变量: {', '.join(missing_vars)}")
    sys.exit(1)

# 打印环境变量加载情况
print("数据库配置信息：")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD'))}")  # 隐藏实际密码
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"环境变量文件路径: {env_path}")

# 应用设置
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# 数据库设置
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
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