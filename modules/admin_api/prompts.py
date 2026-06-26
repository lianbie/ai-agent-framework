"""
提示词管理API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging

from common.postgresql_pool import pg_pool
from modules.admin_api.models import (
    PromptCreate, PromptUpdate, PromptResponse, PromptTestRequest, ApiResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["提示词管理"])


@router.get("", response_model=List[PromptResponse])
async def list_prompts(
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None
):
    """
    获取提示词列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **search**: 搜索关键词
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 构建查询
            query = "SELECT * FROM ai_service.prompts"
            params = []

            if search:
                query += " WHERE name ILIKE %s OR description ILIKE %s"
                params.extend([f"%{search}%", f"%{search}%"])

            query += " ORDER BY is_default DESC, created_at DESC"
            query += " LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [PromptResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取提示词列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=PromptResponse)
async def create_prompt(prompt: PromptCreate):
    """
    创建提示词

    - **name**: 提示词名称（唯一）
    - **system_prompt**: 系统提示词内容
    - **description**: 描述（可选）
    - **variables**: 模板变量（可选）
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 检查名称是否已存在
            cursor.execute(
                "SELECT id FROM ai_service.prompts WHERE name = %s",
                (prompt.name,)
            )
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="提示词名称已存在")

            # 插入新提示词
            cursor.execute(
                """
                INSERT INTO ai_service.prompts (name, description, system_prompt, variables, is_default)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (prompt.name, prompt.description, prompt.system_prompt,
                 prompt.variables, prompt.is_default)
            )
            result = cursor.fetchone()
            pg_pool.get_connection().__enter__().commit()

            return PromptResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 创建提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: int):
    """
    获取单个提示词

    - **prompt_id**: 提示词ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM ai_service.prompts WHERE id = %s",
                (prompt_id,)
            )
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="提示词不存在")

            return PromptResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: int, prompt: PromptUpdate):
    """
    更新提示词

    - **prompt_id**: 提示词ID
    - **name**: 新名称（可选）
    - **system_prompt**: 新提示词内容（可选）
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 检查提示词是否存在
            cursor.execute(
                "SELECT * FROM ai_service.prompts WHERE id = %s",
                (prompt_id,)
            )
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="提示词不存在")

            # 构建更新语句
            updates = []
            params = []

            if prompt.name is not None:
                # 检查新名称是否冲突
                cursor.execute(
                    "SELECT id FROM ai_service.prompts WHERE name = %s AND id != %s",
                    (prompt.name, prompt_id)
                )
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="提示词名称已存在")
                updates.append("name = %s")
                params.append(prompt.name)

            if prompt.description is not None:
                updates.append("description = %s")
                params.append(prompt.description)

            if prompt.system_prompt is not None:
                updates.append("system_prompt = %s")
                params.append(prompt.system_prompt)
                updates.append("version = version + 1")

            if prompt.variables is not None:
                updates.append("variables = %s")
                params.append(prompt.variables)

            if prompt.is_default is not None:
                # 如果设为默认，取消其他默认
                if prompt.is_default:
                    cursor.execute(
                        "UPDATE ai_service.prompts SET is_default = FALSE WHERE is_default = TRUE"
                    )
                updates.append("is_default = %s")
                params.append(prompt.is_default)

            if not updates:
                return PromptResponse(**existing)

            # 执行更新
            params.append(prompt_id)
            query = f"UPDATE ai_service.prompts SET {', '.join(updates)} WHERE id = %s RETURNING *"
            cursor.execute(query, params)
            result = cursor.fetchone()

            # 清除提示词缓存
            from common.prompt_manager import prompt_manager
            prompt_manager.clear_cache()

            return PromptResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 更新提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{prompt_id}", response_model=ApiResponse)
async def delete_prompt(prompt_id: int):
    """
    删除提示词

    - **prompt_id**: 提示词ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 检查是否为默认提示词
            cursor.execute(
                "SELECT is_default FROM ai_service.prompts WHERE id = %s",
                (prompt_id,)
            )
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="提示词不存在")

            if result['is_default']:
                raise HTTPException(status_code=400, detail="不能删除默认提示词")

            # 删除提示词
            cursor.execute(
                "DELETE FROM ai_service.prompts WHERE id = %s",
                (prompt_id,)
            )

            return ApiResponse(success=True, message="提示词已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_prompt(request: PromptTestRequest):
    """
    测试提示词

    - **prompt_id**: 提示词ID
    - **message**: 测试消息
    - **variables**: 变量值（可选）
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 获取提示词
            cursor.execute(
                "SELECT * FROM ai_service.prompts WHERE id = %s",
                (request.prompt_id,)
            )
            prompt = cursor.fetchone()

            if not prompt:
                raise HTTPException(status_code=404, detail="提示词不存在")

            # 替换变量
            system_prompt = prompt['system_prompt']
            if request.variables:
                for key, value in request.variables.items():
                    system_prompt = system_prompt.replace(f"{{{{{key}}}}}", value)

            # 调用LLM测试
            from modules.agents.customer_service_agent import CustomerServiceAgent, AgentConfig

            config = AgentConfig(
                name="测试Agent",
                system_prompt=system_prompt,
                model_id="gpt-4o-mini"
            )
            agent = CustomerServiceAgent(config=config)
            result = await agent.chat(request.message)

            return {
                "success": result.success,
                "reply": result.reply,
                "system_prompt": system_prompt,
                "error": result.error
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 测试提示词失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
