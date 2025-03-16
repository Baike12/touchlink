from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
from pydantic import BaseModel, Field
import json

from backend.src.core.models import AnalyticsTemplate
from backend.src.config.database import get_db
from backend.src.utils.logger import setup_logger

# 创建路由
router = APIRouter(prefix="/analytics-templates", tags=["分析模板"])

# 创建日志记录器
logger = setup_logger("analytics_templates_api")


# 数据模型
class AnalyticsTemplateBase(BaseModel):
    """分析模板基础模型"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    datasource_id: str = Field(..., description="数据源ID")
    tables: List[str] = Field(..., description="选择的表")
    columns: Dict[str, List[str]] = Field(..., description="选择的列")
    join_relationships: Optional[List[Dict[str, Any]]] = Field(None, description="JOIN关系")


class AnalyticsTemplateCreate(AnalyticsTemplateBase):
    """创建分析模板模型"""
    pass


class AnalyticsTemplateUpdate(BaseModel):
    """更新分析模板模型"""
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    tables: Optional[List[str]] = Field(None, description="选择的表")
    columns: Optional[Dict[str, List[str]]] = Field(None, description="选择的列")
    join_relationships: Optional[List[Dict[str, Any]]] = Field(None, description="JOIN关系")


class AnalyticsTemplateResponse(BaseModel):
    """分析模板响应模型"""
    id: str = Field(..., description="模板ID")
    user_id: str = Field(..., description="用户ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    datasource_id: str = Field(..., description="数据源ID")
    tables: List[str] = Field(..., description="选择的表")
    columns: Dict[str, List[str]] = Field(..., description="选择的列")
    join_relationships: Optional[List[Dict[str, Any]]] = Field(None, description="JOIN关系")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True


@router.post("", response_model=AnalyticsTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    template: AnalyticsTemplateCreate,
    db: Session = Depends(get_db)
):
    """
    创建分析模板
    """
    try:
        # 记录请求数据
        logger.info(f"创建模板请求数据: {template.dict()}")
        
        # 验证数据
        if not template.name:
            logger.error("模板名称不能为空")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板名称不能为空"
            )
        
        if not template.datasource_id:
            logger.error("数据源ID不能为空")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="数据源ID不能为空"
            )
        
        # 直接创建模板对象，不进行复杂的JSON转换
        try:
            logger.info("开始创建模板对象")
            
            # 手动转换JSON字段
            tables_json = json.dumps(template.tables)
            columns_json = json.dumps(template.columns)
            join_relationships_json = json.dumps(template.join_relationships) if template.join_relationships else None
            
            # 创建模板对象
            db_template = AnalyticsTemplate(
                name=template.name,
                description=template.description,
                datasource_id=template.datasource_id,
                tables=tables_json,
                columns=columns_json,
                join_relationships=join_relationships_json
            )
            logger.info(f"模板对象创建成功: {db_template}")
        except Exception as e:
            logger.error(f"创建模板对象失败: {str(e)}")
            logger.exception("创建模板对象详细错误:")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建模板对象失败: {str(e)}"
            )
        
        # 保存到数据库
        try:
            logger.info("开始保存模板到数据库")
            db.add(db_template)
            logger.info("模板对象添加到会话成功")
            db.commit()
            logger.info("模板对象提交到数据库成功")
            db.refresh(db_template)
            logger.info("模板对象刷新成功")
        except Exception as e:
            logger.error(f"保存模板到数据库失败: {str(e)}")
            logger.exception("保存模板详细错误:")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"保存模板到数据库失败: {str(e)}"
            )
        
        # 返回响应前，手动构建响应对象
        try:
            response_dict = {
                "id": db_template.id,
                "user_id": db_template.user_id,
                "name": db_template.name,
                "description": db_template.description,
                "datasource_id": db_template.datasource_id,
                "tables": json.loads(db_template.tables),
                "columns": json.loads(db_template.columns),
                "created_at": db_template.created_at.isoformat() if db_template.created_at else None,
                "updated_at": db_template.updated_at.isoformat() if db_template.updated_at else None
            }
            
            if db_template.join_relationships:
                response_dict["join_relationships"] = json.loads(db_template.join_relationships)
            else:
                response_dict["join_relationships"] = None
                
            logger.info(f"创建分析模板成功: {db_template.id}")
            return response_dict
        except Exception as e:
            logger.error(f"构建响应对象失败: {str(e)}")
            logger.exception("构建响应对象详细错误:")
            # 即使构建响应失败，数据已经保存成功，所以不回滚
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"模板已保存，但构建响应失败: {str(e)}"
            )
    
    except HTTPException:
        # 直接重新抛出HTTP异常
        raise
    
    except Exception as e:
        logger.error(f"创建分析模板失败: {str(e)}")
        logger.exception("详细错误信息:")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建分析模板失败: {str(e)}"
        )


@router.get("", response_model=List[AnalyticsTemplateResponse])
def get_templates(
    skip: int = Query(0, description="跳过记录数"),
    limit: int = Query(100, description="返回记录数"),
    datasource_id: Optional[str] = Query(None, description="数据源ID"),
    db: Session = Depends(get_db)
):
    """
    获取分析模板列表
    """
    try:
        # 构建查询
        query = db.query(AnalyticsTemplate)
        
        # 按数据源过滤
        if datasource_id:
            query = query.filter(AnalyticsTemplate.datasource_id == datasource_id)
        
        # 获取总记录数
        total_count = query.count()
        logger.info(f"模板总数: {total_count}")
        
        # 分页 - 增加默认限制
        if limit <= 0:
            limit = 1000  # 设置一个较大的默认值
        
        templates = query.offset(skip).limit(limit).all()
        
        # 手动处理JSON字段
        result = []
        for template in templates:
            try:
                template_dict = {
                    "id": template.id,
                    "user_id": template.user_id,
                    "name": template.name,
                    "description": template.description,
                    "datasource_id": template.datasource_id,
                    "tables": json.loads(template.tables),
                    "columns": json.loads(template.columns),
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "updated_at": template.updated_at.isoformat() if template.updated_at else None
                }
                
                if template.join_relationships:
                    template_dict["join_relationships"] = json.loads(template.join_relationships)
                else:
                    template_dict["join_relationships"] = None
                
                result.append(template_dict)
            except Exception as e:
                logger.error(f"处理模板 {template.id} 失败: {str(e)}")
                # 跳过处理失败的模板
                continue
        
        logger.info(f"获取分析模板列表成功: {len(result)}/{total_count} 条记录")
        return result
    
    except Exception as e:
        logger.error(f"获取分析模板列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析模板列表失败: {str(e)}"
        )


@router.get("/{template_id}", response_model=AnalyticsTemplateResponse)
def get_template(
    template_id: str = Path(..., description="模板ID"),
    db: Session = Depends(get_db)
):
    """
    获取分析模板详情
    """
    try:
        # 查询模板
        template = db.query(AnalyticsTemplate).filter(AnalyticsTemplate.id == template_id).first()
        
        # 检查是否存在
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模板不存在: {template_id}"
            )
        
        # 手动处理JSON字段
        try:
            template_dict = {
                "id": template.id,
                "user_id": template.user_id,
                "name": template.name,
                "description": template.description,
                "datasource_id": template.datasource_id,
                "tables": json.loads(template.tables),
                "columns": json.loads(template.columns),
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None
            }
            
            if template.join_relationships:
                template_dict["join_relationships"] = json.loads(template.join_relationships)
            else:
                template_dict["join_relationships"] = None
        except Exception as e:
            logger.error(f"处理模板 {template.id} 失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"处理模板数据失败: {str(e)}"
            )
        
        logger.info(f"获取分析模板详情成功: {template_id}")
        return template_dict
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"获取分析模板详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析模板详情失败: {str(e)}"
        )


@router.put("/{template_id}", response_model=AnalyticsTemplateResponse)
def update_template(
    template_id: str = Path(..., description="模板ID"),
    template_update: AnalyticsTemplateUpdate = None,
    db: Session = Depends(get_db)
):
    """
    更新分析模板
    """
    try:
        # 查询模板
        db_template = db.query(AnalyticsTemplate).filter(AnalyticsTemplate.id == template_id).first()
        
        # 检查是否存在
        if not db_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模板不存在: {template_id}"
            )
        
        # 更新字段
        if template_update.name is not None:
            db_template.name = template_update.name
        
        if template_update.description is not None:
            db_template.description = template_update.description
        
        if template_update.tables is not None:
            db_template.tables = json.dumps(template_update.tables)
        
        if template_update.columns is not None:
            db_template.columns = json.dumps(template_update.columns)
        
        if template_update.join_relationships is not None:
            db_template.join_relationships = json.dumps(template_update.join_relationships)
        
        # 保存到数据库
        db.commit()
        db.refresh(db_template)
        
        # 手动处理JSON字段
        try:
            template_dict = {
                "id": db_template.id,
                "user_id": db_template.user_id,
                "name": db_template.name,
                "description": db_template.description,
                "datasource_id": db_template.datasource_id,
                "tables": json.loads(db_template.tables),
                "columns": json.loads(db_template.columns),
                "created_at": db_template.created_at.isoformat() if db_template.created_at else None,
                "updated_at": db_template.updated_at.isoformat() if db_template.updated_at else None
            }
            
            if db_template.join_relationships:
                template_dict["join_relationships"] = json.loads(db_template.join_relationships)
            else:
                template_dict["join_relationships"] = None
        except Exception as e:
            logger.error(f"处理模板 {db_template.id} 失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"处理模板数据失败: {str(e)}"
            )
        
        logger.info(f"更新分析模板成功: {template_id}")
        return template_dict
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"更新分析模板失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新分析模板失败: {str(e)}"
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: str = Path(..., description="模板ID"),
    db: Session = Depends(get_db)
):
    """
    删除分析模板
    """
    try:
        # 查询模板
        db_template = db.query(AnalyticsTemplate).filter(AnalyticsTemplate.id == template_id).first()
        
        # 检查是否存在
        if not db_template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"模板不存在: {template_id}"
            )
        
        # 删除模板
        db.delete(db_template)
        db.commit()
        
        logger.info(f"删除分析模板成功: {template_id}")
        return None
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"删除分析模板失败: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除分析模板失败: {str(e)}"
        ) 