from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from backend.src.utils.middleware import exception_handler_middleware
from backend.src.api.v1 import api_router
from backend.src.config.init_db import init_db
from backend.src.config.settings import Settings

# 加载环境变量
load_dotenv()

# 获取设置
settings = Settings()

# 创建FastAPI应用
app = FastAPI(
    title="TouchLink API",
    description="TouchLink数据分析平台API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # 从设置中读取允许的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加异常处理中间件
app.middleware("http")(exception_handler_middleware)

# 注册API路由
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to TouchLink API"}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "ok"}

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()

if __name__ == "__main__":
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    ) 