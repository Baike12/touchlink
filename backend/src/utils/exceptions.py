from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class TouchLinkException(Exception):
    """TouchLink基础异常类"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers


class BadRequestException(TouchLinkException):
    """400错误"""
    
    def __init__(
        self,
        detail: str = "Bad Request",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers
        )


class UnauthorizedException(TouchLinkException):
    """401错误"""
    
    def __init__(
        self,
        detail: str = "Unauthorized",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers
        )


class ForbiddenException(TouchLinkException):
    """403错误"""
    
    def __init__(
        self,
        detail: str = "Forbidden",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers
        )


class NotFoundException(TouchLinkException):
    """404错误"""
    
    def __init__(
        self,
        detail: str = "Not Found",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers
        )


class ConflictException(TouchLinkException):
    """409错误"""
    
    def __init__(
        self,
        detail: str = "Conflict",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers
        )


class InternalServerErrorException(TouchLinkException):
    """500错误"""
    
    def __init__(
        self,
        detail: str = "Internal Server Error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers
        )


class DataSourceException(TouchLinkException):
    """数据源异常"""
    
    def __init__(
        self,
        detail: str = "Data Source Error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers
        )


class AnalyticsException(TouchLinkException):
    """分析引擎异常"""
    
    def __init__(
        self,
        detail: str = "Analytics Error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers
        )


class ResourceNotFoundException(NotFoundException):
    """资源未找到异常"""
    
    def __init__(
        self,
        detail: str = "Resource Not Found",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            headers=headers
        )


class ValidationException(BadRequestException):
    """验证异常"""
    
    def __init__(
        self,
        detail: str = "Validation Error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            headers=headers
        )


class DatabaseException(InternalServerErrorException):
    """数据库异常"""
    
    def __init__(
        self,
        detail: str = "Database Error",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            detail=detail,
            headers=headers
        ) 