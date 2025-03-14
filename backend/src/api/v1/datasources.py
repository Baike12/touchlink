from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator

from src.core.data_sources import DataSourceFactory
from src.core.services import DataSourceService
from src.utils.exceptions import DataSourceException, NotFoundException
from src.config.database import get_db
from src.utils.logger import setup_logger

# 创建路由
router = APIRouter(prefix="/datasources", tags=["数据源"])

# 创建日志记录器
logger = setup_logger("datasources_api")

# 临时数据源连接（用于会话）
_temp_datasource = None
_temp_connection_config = None

# 数据模型
class DataSourceConnectionConfig(BaseModel):
    """数据源连接配置"""
    type: str = Field(..., description="数据源类型，如mysql")
    host: str = Field(..., description="主机地址")
    port: int = Field(..., description="端口")
    user: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    database: str = Field(..., description="数据库名")
    
    class Config:
        schema_extra = {
            "example": {
                "type": "mysql",
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "test"
            }
        }


class DataSourceCreate(BaseModel):
    """创建数据源请求"""
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    config: Dict[str, Any] = Field(..., description="数据源配置")


class DataSourceUpdate(BaseModel):
    """更新数据源请求"""
    name: Optional[str] = Field(None, description="数据源名称")
    config: Optional[Dict[str, Any]] = Field(None, description="数据源配置")


class DataSourceResponse(BaseModel):
    """数据源响应"""
    id: Optional[str] = Field(None, description="数据源ID")
    type: str = Field(..., description="数据源类型")
    name: str = Field(..., description="数据源名称")
    status: str = Field(..., description="状态")
    message: Optional[str] = Field(None, description="消息")


class DataSourceDetail(BaseModel):
    """数据源详情"""
    id: str = Field(..., description="数据源ID")
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class TableListResponse(BaseModel):
    """表列表响应"""
    tables: List[str] = Field(..., description="表名列表")


class TableColumn(BaseModel):
    """表列信息"""
    name: str = Field(..., description="列名")
    type: str = Field(..., description="类型")
    nullable: bool = Field(..., description="是否可为空")
    default: Optional[Any] = Field(None, description="默认值")
    primary_key: bool = Field(..., description="是否为主键")


class TableSchemaResponse(BaseModel):
    """表结构响应"""
    table_name: str = Field(..., description="表名")
    columns: List[TableColumn] = Field(..., description="列信息")


class TableDataResponse(BaseModel):
    """表数据响应"""
    columns: List[str] = Field(..., description="列名")
    data: List[Dict[str, Any]] = Field(..., description="数据")


class DataSourceDetailWithConfig(BaseModel):
    """数据源详情（包含配置）"""
    id: str = Field(..., description="数据源ID")
    name: str = Field(..., description="数据源名称")
    type: str = Field(..., description="数据源类型")
    config: Dict[str, Any] = Field(..., description="数据源配置")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


# 路由定义
@router.get("/types", response_model=List[str])
async def get_datasource_types():
    """获取支持的数据源类型"""
    return DataSourceFactory.get_registered_sources()


@router.post("/test", response_model=DataSourceResponse)
async def test_datasource_connection(config: DataSourceConnectionConfig):
    """测试数据源连接"""
    try:
        # 获取数据源类型
        source_type = config.type
        
        # 测试连接
        connection_config = config.dict()
        success = DataSourceService.test_connection(source_type, connection_config)
        
        if success:
            return DataSourceResponse(
                type=source_type,
                name=f"{connection_config['host']}:{connection_config['port']}/{connection_config['database']}",
                status="success",
                message="连接成功"
            )
        else:
            return DataSourceResponse(
                type=source_type,
                name=f"{connection_config['host']}:{connection_config['port']}/{connection_config['database']}",
                status="error",
                message="连接失败"
            )
    
    except DataSourceException as e:
        logger.error(f"测试数据源连接失败: {str(e)}")
        return DataSourceResponse(
            type=config.type,
            name=f"{config.host}:{config.port}/{config.database}",
            status="error",
            message=str(e)
        )
    except Exception as e:
        logger.error(f"测试数据源连接失败: {str(e)}")
        return DataSourceResponse(
            type=config.type,
            name=f"{config.host}:{config.port}/{config.database}",
            status="error",
            message=f"连接失败: {str(e)}"
        )


@router.post("/", response_model=DataSourceDetail)
async def create_datasource(datasource: DataSourceCreate, db: Session = Depends(get_db)):
    """创建数据源"""
    try:
        # 测试连接
        success = DataSourceService.test_connection(datasource.type, datasource.config)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源连接测试失败"
            )
        
        # 创建数据源
        created = DataSourceService.create_datasource(
            db=db,
            name=datasource.name,
            type=datasource.type,
            config=datasource.config
        )
        
        return DataSourceDetail(
            id=created.id,
            name=created.name,
            type=created.type,
            created_at=created.created_at.isoformat(),
            updated_at=created.updated_at.isoformat()
        )
    
    except Exception as e:
        logger.error(f"创建数据源失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建数据源失败: {str(e)}"
        )


@router.get("/", response_model=List[DataSourceDetail])
async def get_datasources(db: Session = Depends(get_db)):
    """获取所有数据源"""
    try:
        datasources = DataSourceService.get_all_datasources(db)
        
        return [
            DataSourceDetail(
                id=ds.id,
                name=ds.name,
                type=ds.type,
                created_at=ds.created_at.isoformat(),
                updated_at=ds.updated_at.isoformat()
            )
            for ds in datasources
        ]
    
    except Exception as e:
        logger.error(f"获取数据源列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据源列表失败: {str(e)}"
        )


@router.get("/{datasource_id}", response_model=DataSourceDetailWithConfig)
async def get_datasource(
    datasource_id: str = Path(..., description="数据源ID"),
    db: Session = Depends(get_db)
):
    """获取数据源详情"""
    try:
        datasource = DataSourceService.get_datasource(db, datasource_id)
        
        # 解密配置
        config = DataSourceService._decrypt_config(datasource.config)
        
        return DataSourceDetailWithConfig(
            id=datasource.id,
            name=datasource.name,
            type=datasource.type,
            config=config,
            created_at=datasource.created_at.isoformat(),
            updated_at=datasource.updated_at.isoformat()
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取数据源详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据源详情失败: {str(e)}"
        )


@router.put("/{datasource_id}", response_model=DataSourceDetail)
async def update_datasource(
    datasource: DataSourceUpdate,
    datasource_id: str = Path(..., description="数据源ID"),
    db: Session = Depends(get_db)
):
    """更新数据源"""
    try:
        # 如果更新了配置，测试连接
        if datasource.config:
            # 获取数据源类型
            ds = DataSourceService.get_datasource(db, datasource_id)
            
            # 测试连接
            success = DataSourceService.test_connection(ds.type, datasource.config)
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="数据源连接测试失败"
                )
        
        # 更新数据源
        updated = DataSourceService.update_datasource(
            db=db,
            datasource_id=datasource_id,
            name=datasource.name,
            config=datasource.config
        )
        
        return DataSourceDetail(
            id=updated.id,
            name=updated.name,
            type=updated.type,
            created_at=updated.created_at.isoformat(),
            updated_at=updated.updated_at.isoformat()
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"更新数据源失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新数据源失败: {str(e)}"
        )


@router.delete("/{datasource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_datasource(
    datasource_id: str = Path(..., description="数据源ID"),
    db: Session = Depends(get_db)
):
    """删除数据源"""
    try:
        DataSourceService.delete_datasource(db, datasource_id)
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"删除数据源失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除数据源失败: {str(e)}"
        )


@router.post("/connect", response_model=DataSourceResponse)
async def connect_datasource(config: DataSourceConnectionConfig, db: Session = Depends(get_db)):
    """连接数据源（临时连接，不保存）"""
    try:
        # 获取数据源类型
        source_type = config.type
        
        # 创建数据源实例
        datasource = DataSourceFactory.create(source_type)
        if not datasource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的数据源类型: {source_type}"
            )
        
        # 连接数据源
        connection_config = config.dict()
        success = datasource.connect(connection_config)
        
        if success:
            # 将连接的数据源保存到全局变量中，供后续API调用使用
            # 注意：在生产环境中，应该使用更安全的方式来管理会话状态
            global _temp_datasource, _temp_connection_config
            _temp_datasource = datasource
            _temp_connection_config = connection_config
            
            return DataSourceResponse(
                type=source_type,
                name=f"{connection_config['host']}:{connection_config['port']}/{connection_config['database']}",
                status="success",
                message="连接成功"
            )
        else:
            return DataSourceResponse(
                type=source_type,
                name=f"{connection_config['host']}:{connection_config['port']}/{connection_config['database']}",
                status="error",
                message="连接失败"
            )
    
    except Exception as e:
        logger.error(f"连接数据源失败: {str(e)}")
        return DataSourceResponse(
            type=config.type,
            name=f"{config.host}:{config.port}/{config.database}",
            status="error",
            message=str(e)
        )


@router.get("/session/tables", response_model=TableListResponse)
async def get_temp_tables(db: Session = Depends(get_db)):
    """获取临时连接的表列表"""
    try:
        # 检查是否有临时连接的数据源
        if not _temp_datasource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未连接数据源，请先连接数据源"
            )
        
        # 获取表列表
        tables = _temp_datasource.get_tables()
        
        return TableListResponse(tables=tables)
    
    except Exception as e:
        logger.error(f"获取临时连接表列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表列表失败: {str(e)}"
        )


@router.get("/tables/{table_name}/schema", response_model=TableSchemaResponse)
async def get_temp_table_schema(
    table_name: str = Path(..., description="表名"),
    db: Session = Depends(get_db)
):
    """获取临时连接的表结构"""
    try:
        # 检查是否有临时连接的数据源
        if not _temp_datasource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未连接数据源，请先连接数据源"
            )
        
        # 获取表结构
        columns = _temp_datasource.get_table_schema(table_name)
        
        return TableSchemaResponse(table_name=table_name, columns=columns)
    
    except Exception as e:
        logger.error(f"获取临时连接表结构失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表结构失败: {str(e)}"
        )


@router.get("/{datasource_id}/tables", response_model=TableListResponse)
async def get_tables(
    datasource_id: str = Path(..., description="数据源ID"),
    db: Session = Depends(get_db)
):
    """获取数据源中的表列表"""
    try:
        tables = DataSourceService.get_tables(datasource_id, db)
        return TableListResponse(tables=tables)
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DataSourceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取表列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表列表失败: {str(e)}"
        )


@router.get("/{datasource_id}/tables/{table_name}/schema", response_model=TableSchemaResponse)
async def get_table_schema(
    datasource_id: str = Path(..., description="数据源ID"),
    table_name: str = Path(..., description="表名"),
    db: Session = Depends(get_db)
):
    """获取表结构"""
    try:
        schema = DataSourceService.get_table_schema(datasource_id, table_name, db)
        return TableSchemaResponse(
            table_name=table_name,
            columns=[TableColumn(**col) for col in schema]
        )
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DataSourceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取表结构失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表结构失败: {str(e)}"
        )


@router.get("/{datasource_id}/tables/{table_name}/data", response_model=TableDataResponse)
async def get_table_data(
    datasource_id: str = Path(..., description="数据源ID"),
    table_name: str = Path(..., description="表名"),
    limit: int = Query(100, description="返回的最大行数"),
    db: Session = Depends(get_db)
):
    """获取表数据"""
    try:
        data = DataSourceService.get_sample_data(datasource_id, table_name, limit, db)
        return TableDataResponse(**data)
    
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DataSourceException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"获取表数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表数据失败: {str(e)}"
        ) 

@router.get("/tables/{table_name}/data", response_model=TableDataResponse)
async def get_temp_table_data(
    table_name: str = Path(..., description="表名"),
    limit: int = Query(100, description="返回的最大行数"),
    db: Session = Depends(get_db)
):
    """获取临时连接的表数据"""
    try:
        # 检查是否有临时连接的数据源
        if not _temp_datasource:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未连接数据源，请先连接数据源"
            )
        
        # 获取表结构以获取列名
        columns_info = _temp_datasource.get_table_schema(table_name)
        columns = [col["name"] for col in columns_info]
        
        # 构建查询参数
        query = {
            "table_name": table_name,
            "limit": limit
        }
        
        # 获取表数据
        df = _temp_datasource.get_sample_data(table_name, limit)
        
        # 将DataFrame转换为字典列表
        data = df.to_dict(orient="records")
        
        return TableDataResponse(columns=columns, data=data)
    
    except Exception as e:
        logger.error(f"获取临时连接表数据失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取表数据失败: {str(e)}"
        )