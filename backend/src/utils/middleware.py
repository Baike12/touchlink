from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import TouchLinkException
import logging
import traceback
from typing import Callable

# 配置日志
logger = logging.getLogger(__name__)


async def exception_handler_middleware(request: Request, call_next: Callable):
    """
    异常处理中间件
    捕获所有未处理的异常，并返回统一的错误响应
    """
    try:
        return await call_next(request)
    except TouchLinkException as exc:
        # 处理自定义异常
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
    except Exception as exc:
        # 处理未预期的异常
        logger.error(f"Unexpected error: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"}
        ) 