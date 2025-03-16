from typing import Generator, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.user import User

# 简化的获取当前用户函数
async def get_current_user():
    """
    返回一个模拟用户，简化开发
    
    Returns:
        User: 模拟用户信息
    """
    return User(
        id="1",
        username="admin",
        email="admin@example.com",
        is_active=True,
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00"
    )

# 简化的获取当前活跃用户函数
async def get_current_active_user():
    """
    返回一个模拟活跃用户，简化开发
    
    Returns:
        User: 模拟用户信息
    """
    return await get_current_user() 