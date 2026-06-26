"""
系统监控API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging
import time
import psutil

from common.postgresql_pool import pg_pool
from modules.admin_api.models import SystemStats, SystemLog, HealthCheck

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitor", tags=["系统监控"])

# 记录启动时间
_start_time = time.time()


@router.get("/stats", response_model=SystemStats)
async def get_stats():
    """
    获取系统统计
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 总对话数
            cursor.execute("SELECT COUNT(*) as total FROM ai_service.conversations")
            total_conversations = cursor.fetchone()['total']

            # 总文档数
            cursor.execute("SELECT COUNT(*) as total FROM ai_service.knowledge_documents")
            total_documents = cursor.fetchone()['total']

            # 总提示词数
            cursor.execute("SELECT COUNT(*) as total FROM ai_service.prompts")
            total_prompts = cursor.fetchone()['total']

            # 总模型数
            cursor.execute("SELECT COUNT(*) as total FROM ai_service.model_configs")
            total_models = cursor.fetchone()['total']

            # 今日API调用数
            cursor.execute(
                """
                SELECT COUNT(*) as total FROM ai_service.conversations
                WHERE created_at >= CURRENT_DATE
                """
            )
            api_calls_today = cursor.fetchone()['total']

            # 平均响应时间
            cursor.execute(
                """
                SELECT COALESCE(AVG(duration_ms), 0) as avg_time
                FROM ai_service.conversations
                WHERE duration_ms > 0
                """
            )
            avg_response_time = cursor.fetchone()['avg_time']

            # 错误率（通过检查metadata中的error字段）
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total,
                    COUNT(CASE WHEN metadata->>'error' IS NOT NULL THEN 1 END) as errors
                FROM ai_service.conversations
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
                """
            )
            stats = cursor.fetchone()
            error_rate = (stats['errors'] / stats['total'] * 100) if stats['total'] > 0 else 0

            return SystemStats(
                total_conversations=total_conversations,
                total_documents=total_documents,
                total_prompts=total_prompts,
                total_models=total_models,
                api_calls_today=api_calls_today,
                avg_response_time_ms=avg_response_time,
                error_rate=round(error_rate, 2)
            )

    except Exception as e:
        logger.error(f"❌ 获取系统统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs", response_model=List[SystemLog])
async def get_logs(
    level: Optional[str] = None,
    module: Optional[str] = None,
    page: int = 1,
    page_size: int = 100
):
    """
    获取系统日志

    - **level**: 日志级别过滤 (DEBUG, INFO, WARNING, ERROR)
    - **module**: 模块过滤
    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            query = "SELECT * FROM ai_service.system_logs"
            params = []
            conditions = []

            if level:
                conditions.append("level = %s")
                params.append(level)

            if module:
                conditions.append("module ILIKE %s")
                params.append(f"%{module}%")

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [SystemLog(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取系统日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    健康检查
    """
    uptime = int(time.time() - _start_time)

    # 检查数据库
    db_ok = False
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute("SELECT 1")
            db_ok = True
    except Exception:
        pass

    # 检查Redis
    redis_ok = False
    try:
        from common.redis_client import redis_client
        redis_ok = redis_client.health_check()
    except Exception:
        pass

    # 检查向量存储
    vector_ok = False
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute("SELECT 1 FROM ai_service.knowledge_documents LIMIT 1")
            vector_ok = True
    except Exception:
        pass

    status = "ok" if (db_ok and redis_ok) else "degraded"

    return HealthCheck(
        status=status,
        version="2.0.0",
        uptime_seconds=uptime,
        database=db_ok,
        redis=redis_ok,
        vector_store=vector_ok
    )


@router.get("/performance")
async def get_performance():
    """
    获取性能指标
    """
    try:
        process = psutil.Process()

        # CPU使用率
        cpu_percent = process.cpu_percent(interval=0.1)

        # 内存使用
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        # 系统信息
        system_cpu = psutil.cpu_percent()
        system_memory = psutil.virtual_memory()

        return {
            "process": {
                "cpu_percent": cpu_percent,
                "memory_mb": round(memory_mb, 2),
                "threads": process.num_threads()
            },
            "system": {
                "cpu_percent": system_cpu,
                "memory_total_mb": round(system_memory.total / 1024 / 1024, 2),
                "memory_used_mb": round(system_memory.used / 1024 / 1024, 2),
                "memory_percent": system_memory.percent
            }
        }

    except Exception as e:
        logger.error(f"❌ 获取性能指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
