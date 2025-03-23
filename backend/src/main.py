from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from src.utils.middleware import exception_handler_middleware
from src.config.settings import CORS_ORIGINS, UPLOAD_DIR
from src.api.v1 import api_router
from src.config.init_db import init_db
from src.config.settings import Settings
from starlette.middleware.base import BaseHTTPMiddleware

# 加载环境变量
load_dotenv()

# 获取设置
settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title="TouchLink API",
    description="TouchLink后端API服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加异常处理中间件
class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await exception_handler_middleware(request, call_next)

app.add_middleware(ExceptionMiddleware)

# 注册路由
app.include_router(api_router, prefix="/api")

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Welcome to TouchLink API"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok", "message": "服务正常运行"}

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 