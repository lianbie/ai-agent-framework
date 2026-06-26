"""
智能客服API路由

提供基于agno框架的通用智能问答接口。
企业级设计：完整的错误处理、日志记录、健康检查。
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import time
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent", tags=["智能客服"])


# ============ 请求/响应模型 ============

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(
        ...,
        description="用户消息",
        min_length=1,
        max_length=2000,
        examples=["你好，请介绍一下自己"]
    )
    user_id: str = Field(
        default="default",
        description="用户ID",
        max_length=100
    )
    session_id: Optional[str] = Field(
        default=None,
        description="会话ID（用于多轮对话）",
        max_length=100
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="对话历史",
        max_length=20  # 最多20轮历史
    )
    use_knowledge_base: Optional[bool] = Field(
        default=None,
        description="是否使用知识库（默认使用配置值）"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "你好，请介绍一下自己",
                "user_id": "user_123",
                "use_knowledge_base": True
            }
        }


class ChatResponse(BaseModel):
    """聊天响应"""
    success: bool = Field(description="是否成功")
    reply: str = Field(description="回复内容")
    agent_used: str = Field(default="", description="使用的Agent名称")
    has_knowledge: bool = Field(default=False, description="是否使用了知识库")
    user_id: str = Field(default="", description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    duration_ms: int = Field(default=0, description="处理耗时（毫秒）")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="版本号")
    agent_name: str = Field(description="Agent名称")
    uptime_seconds: int = Field(description="运行时间（秒）")


class AgentInfoResponse(BaseModel):
    """Agent信息响应"""
    name: str
    description: str
    type: str
    model: str
    temperature: float
    max_tokens: int
    enable_knowledge: bool
    enable_history: bool
    has_knowledge_base: bool


# ============ 全局状态 ============

_agent_instance = None
_start_time = time.time()


def get_agent(reset: bool = False):
    """
    获取Agent单例

    Args:
        reset: 是否重置Agent（用于切换模型后）
    """
    global _agent_instance

    if _agent_instance is None or reset:
        from modules.agents.customer_service_agent import CustomerServiceAgent, AgentConfig

        config = AgentConfig(
            name="智能客服",
            description="基于知识库的智能问答客服"
        )
        _agent_instance = CustomerServiceAgent(config=config)
        logger.info("✅ Agent已重新初始化")

    return _agent_instance


# ============ API端点 ============

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    智能问答接口

    基于agno框架的智能客服，支持知识库增强。

    - **message**: 用户消息（必填）
    - **user_id**: 用户ID（可选）
    - **session_id**: 会话ID（可选，用于多轮对话）
    - **conversation_history**: 对话历史（可选）
    - **use_knowledge_base**: 是否使用知识库（可选）
    """
    try:
        agent = get_agent()
        result = await agent.chat(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            conversation_history=request.conversation_history,
            use_knowledge_base=request.use_knowledge_base
        )
        return ChatResponse(**result.to_dict())

    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "reply": "抱歉，服务出现异常，请稍后重试。",
                "error": str(e)
            }
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    流式智能问答接口

    基于agno框架的智能客服，支持流式输出。

    - **message**: 用户消息（必填）
    - **user_id**: 用户ID（可选）
    - **session_id**: 会话ID（可选）
    - **conversation_history**: 对话历史（可选）
    - **use_knowledge_base**: 是否使用知识库（可选）
    """
    try:
        agent = get_agent()

        async def generate():
            async for chunk in agent.stream_chat(
                message=request.message,
                user_id=request.user_id,
                session_id=request.session_id,
                conversation_history=request.conversation_history,
                use_knowledge_base=request.use_knowledge_base
            ):
                # SSE格式
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        logger.error(f"❌ Stream chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    健康检查

    返回服务状态、版本号和运行时间。
    """
    try:
        agent = get_agent()
        uptime = int(time.time() - _start_time)

        return HealthResponse(
            status="ok",
            version="2.0.0",
            agent_name=agent.config.name,
            uptime_seconds=uptime
        )
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return HealthResponse(
            status="error",
            version="2.0.0",
            agent_name="unknown",
            uptime_seconds=0
        )


@router.get("/info", response_model=AgentInfoResponse)
async def info():
    """
    获取Agent信息

    返回Agent的配置信息，包括模型、参数等。
    """
    try:
        agent = get_agent()
        return AgentInfoResponse(**agent.get_info())
    except Exception as e:
        logger.error(f"❌ Info endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset():
    """
    重置Agent

    重新初始化Agent实例（用于切换模型或提示词后）。
    """
    try:
        # 清除模型缓存
        from common.model_manager import model_manager
        model_manager.clear_cache()

        # 清除提示词缓存
        from common.prompt_manager import prompt_manager
        prompt_manager.clear_cache()

        # 重置Agent
        agent = get_agent(reset=True)

        # 获取当前模型信息
        model_info = model_manager.get_current_model_info()

        return {
            "success": True,
            "message": "Agent已重置（模型+提示词）",
            "model": model_info
        }
    except Exception as e:
        logger.error(f"❌ Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 会话管理API ============

@router.get("/sessions")
async def get_sessions(user_id: str = "default"):
    """
    获取用户的会话列表

    - **user_id**: 用户ID
    """
    try:
        from common.conversation_manager import conversation_manager
        sessions = conversation_manager.get_user_sessions(user_id)
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"❌ 获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str, limit: int = 50):
    """
    获取会话历史

    - **session_id**: 会话ID
    - **limit**: 返回条数
    """
    try:
        from common.conversation_manager import conversation_manager
        history = conversation_manager.get_history(session_id, limit)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        logger.error(f"❌ 获取会话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除会话

    - **session_id**: 会话ID
    """
    try:
        from common.conversation_manager import conversation_manager
        success = conversation_manager.delete_session(session_id)
        return {"success": success, "message": "会话已删除"}
    except Exception as e:
        logger.error(f"❌ 删除会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/new")
async def create_session(user_id: str = "default"):
    """
    创建新会话

    - **user_id**: 用户ID
    """
    try:
        from common.conversation_manager import conversation_manager
        session_id = conversation_manager.create_session(user_id)
        return {"session_id": session_id, "user_id": user_id}
    except Exception as e:
        logger.error(f"❌ 创建会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
