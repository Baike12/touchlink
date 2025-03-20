from fastapi import APIRouter

from .datasources import router as datasources_router
from .upload import router as upload_router
from .analytics import router as analytics_router
from .exports import router as exports_router
from .visualizations import router as visualizations_router
from .dashboards import router as dashboards_router
from .charts import router as charts_router
from .analytics_templates import router as analytics_templates_router
from .user_tables import router as user_tables_router

# 创建API路由
api_router = APIRouter(prefix="/v1")

# 注册路由
api_router.include_router(datasources_router)
api_router.include_router(upload_router)
api_router.include_router(analytics_router)
api_router.include_router(exports_router)
api_router.include_router(visualizations_router)
api_router.include_router(dashboards_router)
api_router.include_router(charts_router)
api_router.include_router(analytics_templates_router)
api_router.include_router(user_tables_router)

# 后续会添加更多路由

__all__ = ["api_router"]