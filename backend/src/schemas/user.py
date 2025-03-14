from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="电子邮箱")
    is_active: bool = Field(True, description="是否激活")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, description="用户名")
    email: Optional[str] = Field(None, description="电子邮箱")
    password: Optional[str] = Field(None, description="密码")
    is_active: Optional[bool] = Field(None, description="是否激活")


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class User(UserInDB):
    """用户响应模型"""
    pass


class Token(BaseModel):
    """令牌模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")


class TokenPayload(BaseModel):
    """令牌载荷模型"""
    sub: Optional[str] = Field(None, description="主题（用户ID）")
    exp: Optional[int] = Field(None, description="过期时间") 