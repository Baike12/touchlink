from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import Dict, Any
import os
import uuid
from src.utils.logger import setup_logger
from src.core.data_sources import DataSourceFactory
from src.config.settings import UPLOAD_DIR

# 创建路由
router = APIRouter(prefix="/upload", tags=["文件上传"])

# 创建日志记录器
logger = setup_logger("upload_api")

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/excel", response_model=Dict[str, Any])
async def upload_excel_file(file: UploadFile = File(...)):
    """
    上传Excel文件并导入到MySQL数据库
    
    Args:
        file: 上传的Excel文件
        
    Returns:
        Dict[str, Any]: 上传结果，包含文件路径和表名
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.xls', '.xlsx', '.xlsm')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不支持的文件类型，请上传Excel文件"
            )
        
        # 生成唯一的文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 获取不带扩展名的原始文件名作为表名
        table_name = os.path.splitext(file.filename)[0].lower()
        # 替换非法字符
        table_name = ''.join(c if c.isalnum() else '_' for c in table_name)
        
        # 创建Excel数据源实例
        excel_source = DataSourceFactory.create("excel")
        if not excel_source:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建Excel数据源失败"
            )
        
        # 连接并导入数据
        config = {
            "file_path": file_path,
            "table_name": table_name
        }
        
        success = excel_source.connect(config)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="导入Excel数据失败"
            )
        
        logger.info(f"Excel文件 {file.filename} 已成功上传并导入到MySQL表 {table_name}")
        
        return {
            "file_path": file_path,
            "table_name": table_name,
            "original_filename": file.filename,
            "message": "文件上传并导入成功"
        }
        
    except Exception as e:
        logger.error(f"上传Excel文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传Excel文件失败: {str(e)}"
        ) 