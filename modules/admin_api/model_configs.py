"""
模型配置管理API
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging
import json

from common.postgresql_pool import pg_pool
from modules.admin_api.models import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    ModelTestRequest, ApiResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["模型配置"])


@router.get("", response_model=List[ModelConfigResponse])
async def list_models(
    provider: Optional[str] = None,
    is_active: Optional[bool] = None
):
    """
    获取模型列表

    - **provider**: 提供商过滤
    - **is_active**: 是否激活
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            query = "SELECT * FROM ai_service.model_configs"
            params = []
            conditions = []

            if provider:
                conditions.append("provider = %s")
                params.append(provider)

            if is_active is not None:
                conditions.append("is_active = %s")
                params.append(is_active)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY is_active DESC, created_at DESC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [ModelConfigResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取模型列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ModelConfigResponse)
async def create_model(model: ModelConfigCreate):
    """
    创建模型配置

    - **name**: 模型名称
    - **provider**: 提供商
    - **model_id**: 模型ID
    - **base_url**: API地址
    - **api_key**: API密钥
    - **parameters**: 模型参数
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ai_service.model_configs
                (name, provider, model_id, base_url, api_key_encrypted, parameters)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (model.name, model.provider, model.model_id,
                 model.base_url, model.api_key, json.dumps(model.parameters or {}))
            )
            result = cursor.fetchone()

            return ModelConfigResponse(**result)

    except Exception as e:
        logger.error(f"❌ 创建模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{model_id}", response_model=ModelConfigResponse)
async def get_model(model_id: int):
    """
    获取单个模型配置

    - **model_id**: 模型配置ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ai_service.model_configs WHERE id = %s",
                (model_id,)
            )
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="模型配置不存在")

            return ModelConfigResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{model_id}", response_model=ModelConfigResponse)
async def update_model(model_id: int, model: ModelConfigUpdate):
    """
    更新模型配置

    - **model_id**: 模型配置ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 检查是否存在
            cursor.execute(
                "SELECT * FROM ai_service.model_configs WHERE id = %s",
                (model_id,)
            )
            existing = cursor.fetchone()

            if not existing:
                raise HTTPException(status_code=404, detail="模型配置不存在")

            # 构建更新语句
            updates = []
            params = []

            if model.name is not None:
                updates.append("name = %s")
                params.append(model.name)

            if model.provider is not None:
                updates.append("provider = %s")
                params.append(model.provider)

            if model.model_id is not None:
                updates.append("model_id = %s")
                params.append(model.model_id)

            if model.base_url is not None:
                updates.append("base_url = %s")
                params.append(model.base_url)

            if model.api_key is not None and model.api_key.strip() != "":
                updates.append("api_key_encrypted = %s")
                params.append(model.api_key)

            if model.parameters is not None:
                updates.append("parameters = %s")
                params.append(json.dumps(model.parameters))

            if model.is_active is not None:
                # 如果设为激活，取消其他激活
                if model.is_active:
                    cursor.execute(
                        """
                        UPDATE ai_service.model_configs
                        SET is_active = FALSE
                        WHERE provider = %s AND is_active = TRUE
                        """,
                        (existing['provider'],)
                    )
                updates.append("is_active = %s")
                params.append(model.is_active)

            if not updates:
                return ModelConfigResponse(**existing)

            params.append(model_id)
            query = f"UPDATE ai_service.model_configs SET {', '.join(updates)} WHERE id = %s RETURNING *"
            cursor.execute(query, params)
            result = cursor.fetchone()

            return ModelConfigResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{model_id}", response_model=ApiResponse)
async def delete_model(model_id: int):
    """
    删除模型配置

    - **model_id**: 模型配置ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 检查是否为激活模型
            cursor.execute(
                "SELECT is_active FROM ai_service.model_configs WHERE id = %s",
                (model_id,)
            )
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="模型配置不存在")

            if result['is_active']:
                raise HTTPException(status_code=400, detail="不能删除激活的模型")

            # 删除
            cursor.execute(
                "DELETE FROM ai_service.model_configs WHERE id = %s",
                (model_id,)
            )

            return ApiResponse(success=True, message="模型配置已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除模型配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{model_id}/activate", response_model=ApiResponse)
async def activate_model(model_id: int):
    """
    激活模型

    - **model_id**: 模型配置ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 获取模型信息
            cursor.execute(
                "SELECT * FROM ai_service.model_configs WHERE id = %s",
                (model_id,)
            )
            model = cursor.fetchone()

            if not model:
                raise HTTPException(status_code=404, detail="模型配置不存在")

            # 取消同提供商的其他激活模型
            cursor.execute(
                """
                UPDATE ai_service.model_configs
                SET is_active = FALSE
                WHERE provider = %s AND is_active = TRUE
                """,
                (model['provider'],)
            )

            # 激活当前模型
            cursor.execute(
                "UPDATE ai_service.model_configs SET is_active = TRUE WHERE id = %s",
                (model_id,)
            )

            # 清除模型缓存，让Agent重新读取配置
            from common.model_manager import model_manager
            model_manager.clear_cache()

            return ApiResponse(
                success=True,
                message=f"模型 {model['name']} 已激活，请调用 /api/agent/reset 使配置生效"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 激活模型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_model(request: ModelTestRequest):
    """
    测试模型调用

    - **model_id**: 模型配置ID
    - **message**: 测试消息
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 获取模型配置
            cursor.execute(
                "SELECT * FROM ai_service.model_configs WHERE id = %s",
                (request.model_id,)
            )
            model = cursor.fetchone()

            if not model:
                raise HTTPException(status_code=404, detail="模型配置不存在")

            # 创建Agent测试
            from modules.agents.customer_service_agent import CustomerServiceAgent, AgentConfig
            from agno.models.openai import OpenAIChat

            # 创建模型实例
            llm = OpenAIChat(
                id=model['model_id'],
                base_url=model.get('base_url'),
                api_key=model.get('api_key_encrypted'),
                **model.get('parameters', {})
            )

            config = AgentConfig(
                name="模型测试",
                system_prompt="你是一个AI助手，请简洁地回答用户问题。",
                model_id=model['model_id']
            )

            agent = CustomerServiceAgent(config=config, llm_client=llm)
            result = await agent.chat(request.message)

            return {
                "success": result.success,
                "reply": result.reply,
                "model": model['name'],
                "duration_ms": result.duration_ms,
                "error": result.error
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 测试模型失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
