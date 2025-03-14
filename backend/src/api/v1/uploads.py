from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
import shutil
from datetime import datetime

from src.config.settings import settings
from src.utils.logger import setup_logger

# 创建路由
router = APIRouter(prefix="/uploads", tags=["文件上传"])

# 创建日志记录器
logger = setup_logger("uploads_api")

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/excel", status_code=status.HTTP_201_CREATED)
async def upload_excel_file(file: UploadFile = File(...)):
    """上传Excel文件"""
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xls', '.xlsx', '.xlsm')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只支持Excel文件(.xls, .xlsx, .xlsm)"
            )
        
        # 检查文件大小
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # 重置文件指针
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制: {file_size} > {settings.MAX_UPLOAD_SIZE}"
            )
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # 构建保存路径
        today = datetime.now().strftime("%Y%m%d")
        save_dir = os.path.join(settings.UPLOAD_DIR, today)
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        logger.info(f"上传Excel文件成功: {file.filename} -> {file_path}")
        
        # 返回文件信息
        return {
            "filename": file.filename,
            "file_path": file_path,
            "file_size": file_size,
            "content_type": file.content_type
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传Excel文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )
    finally:
        await file.close() 