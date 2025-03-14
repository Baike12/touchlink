from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from src.utils.middleware import exception_handler_middleware
from src.api.v1 import api_router
from src.config.init_db import init_db

# 加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="TouchLink API",
    description="TouchLink数据分析平台API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为特定的前端域名
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
    return {"status": "healthy"}

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    init_db()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True
    ) 