from typing import Dict, Any, List, Optional
import pandas as pd
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.utils.exceptions import NotFoundException, DataSourceException
from backend.src.utils.logger import setup_logger

# 创建日志记录器
logger = setup_logger("export_service")

# 导出格式
EXPORT_FORMATS = {
    "excel": ".xlsx",
    "csv": ".csv"
}

# 导出目录
EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


class ExportService:
    """导出服务"""
    
    @staticmethod
    def export_dataframe(
        df: pd.DataFrame,
        format: str,
        filename: Optional[str] = None,
        sheet_name: str = "Sheet1",
        **kwargs
    ) -> str:
        """
        导出DataFrame
        
        Args:
            df: 数据框
            format: 导出格式，支持excel和csv
            filename: 文件名，不包含扩展名
            sheet_name: Excel工作表名称
            **kwargs: 其他导出参数
            
        Returns:
            str: 导出文件路径
            
        Raises:
            ValueError: 不支持的导出格式
        """
        # 检查导出格式
        if format not in EXPORT_FORMATS:
            raise ValueError(f"不支持的导出格式: {format}")
        
        # 生成文件名
        if not filename:
            filename = f"export_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 添加扩展名
        file_path = os.path.join(EXPORT_DIR, f"{filename}{EXPORT_FORMATS[format]}")
        
        # 导出数据
        try:
            if format == "excel":
                df.to_excel(file_path, sheet_name=sheet_name, index=False, **kwargs)
            elif format == "csv":
                df.to_csv(file_path, index=False, **kwargs)
            
            logger.info(f"数据导出成功: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            raise
    
    @staticmethod
    def export_multiple_dataframes(
        dataframes: Dict[str, pd.DataFrame],
        format: str,
        filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        导出多个DataFrame
        
        Args:
            dataframes: 数据框字典，键为工作表名称，值为数据框
            format: 导出格式，支持excel和csv
            filename: 文件名，不包含扩展名
            **kwargs: 其他导出参数
            
        Returns:
            str: 导出文件路径
            
        Raises:
            ValueError: 不支持的导出格式
        """
        # 检查导出格式
        if format not in EXPORT_FORMATS:
            raise ValueError(f"不支持的导出格式: {format}")
        
        # 生成文件名
        if not filename:
            filename = f"export_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 添加扩展名
        file_path = os.path.join(EXPORT_DIR, f"{filename}{EXPORT_FORMATS[format]}")
        
        # 导出数据
        try:
            if format == "excel":
                with pd.ExcelWriter(file_path) as writer:
                    for sheet_name, df in dataframes.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False, **kwargs)
            elif format == "csv":
                # 对于CSV，只能导出一个数据框，使用第一个
                if dataframes:
                    first_key = list(dataframes.keys())[0]
                    dataframes[first_key].to_csv(file_path, index=False, **kwargs)
                    
                    # 如果有多个数据框，创建多个CSV文件
                    if len(dataframes) > 1:
                        for sheet_name, df in list(dataframes.items())[1:]:
                            sheet_path = os.path.join(EXPORT_DIR, f"{filename}_{sheet_name}{EXPORT_FORMATS[format]}")
                            df.to_csv(sheet_path, index=False, **kwargs)
            
            logger.info(f"多个数据框导出成功: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"多个数据框导出失败: {str(e)}")
            raise
    
    @staticmethod
    def create_export_template(
        columns: List[str],
        format: str,
        filename: Optional[str] = None,
        sheet_name: str = "Template",
        **kwargs
    ) -> str:
        """
        创建导出模板
        
        Args:
            columns: 列名列表
            format: 导出格式，支持excel和csv
            filename: 文件名，不包含扩展名
            sheet_name: Excel工作表名称
            **kwargs: 其他导出参数
            
        Returns:
            str: 导出文件路径
            
        Raises:
            ValueError: 不支持的导出格式
        """
        # 创建空的DataFrame
        df = pd.DataFrame(columns=columns)
        
        # 导出模板
        return ExportService.export_dataframe(
            df=df,
            format=format,
            filename=filename,
            sheet_name=sheet_name,
            **kwargs
        )
    
    @staticmethod
    def get_export_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取导出文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 文件信息
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件信息
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_name)[1]
        created_time = datetime.fromtimestamp(os.path.getctime(file_path))
        
        return {
            "name": file_name,
            "path": file_path,
            "size": file_size,
            "type": file_type,
            "created_at": created_time.isoformat()
        }
    
    @staticmethod
    def list_export_files() -> List[Dict[str, Any]]:
        """
        列出所有导出文件
        
        Returns:
            List[Dict[str, Any]]: 文件信息列表
        """
        files = []
        
        # 遍历导出目录
        for file_name in os.listdir(EXPORT_DIR):
            file_path = os.path.join(EXPORT_DIR, file_name)
            
            # 只处理文件
            if os.path.isfile(file_path):
                try:
                    files.append(ExportService.get_export_file_info(file_path))
                except:
                    # 忽略无法获取信息的文件
                    pass
        
        return files
    
    @staticmethod
    def delete_export_file(file_path: str) -> None:
        """
        删除导出文件
        
        Args:
            file_path: 文件路径
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 删除文件
        os.remove(file_path)
        logger.info(f"文件已删除: {file_path}") 