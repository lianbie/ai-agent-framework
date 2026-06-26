"""
管理后台API路由入口
"""

from fastapi import APIRouter
from modules.admin_api.prompts import router as prompts_router
from modules.admin_api.knowledge import router as knowledge_router
from modules.admin_api.model_configs import router as models_router
from modules.admin_api.conversations import router as conversations_router
from modules.admin_api.monitor import router as monitor_router

# 创建主路由
router = APIRouter(prefix="/api/admin", tags=["管理后台"])

# 注册子路由
router.include_router(prompts_router)
router.include_router(knowledge_router)
router.include_router(models_router)
router.include_router(conversations_router)
router.include_router(monitor_router)


@router.get("/")
async def admin_index():
    """
    管理后台首页
    """
    return {
        "message": "AI智能客服管理后台",
        "version": "2.0.0",
        "endpoints": {
            "prompts": "/api/admin/prompts",
            "knowledge": "/api/admin/knowledge",
            "models": "/api/admin/models",
            "conversations": "/api/admin/conversations",
            "monitor": "/api/admin/monitor"
        }
    }
