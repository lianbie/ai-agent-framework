"""
通用智能客服Agent - 基于agno框架

提供知识库增强的智能问答能力，可复用于任何行业。
企业级设计：支持配置化、可扩展、可观测。

Usage:
    from modules.agents.customer_service_agent import CustomerServiceAgent, AgentConfig

    # 基础用法
    agent = CustomerServiceAgent()
    result = await agent.chat("你好")

    # 自定义配置
    config = AgentConfig(
        name="电商客服",
        system_prompt="你是一个专业的电商客服...",
        model_id="gpt-4o"
    )
    agent = CustomerServiceAgent(config=config)

    # 带知识库
    agent = CustomerServiceAgent(config=config, knowledge_base=kb)
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Agent类型枚举"""
    CUSTOMER_SERVICE = "customer_service"
    SALES = "sales"
    SUPPORT = "support"
    CUSTOM = "custom"


@dataclass
class AgentConfig:
    """
    Agent配置

    Attributes:
        name: Agent名称
        description: Agent描述
        agent_type: Agent类型
        system_prompt: 系统提示词
        model_id: 模型ID
        temperature: 温度参数
        max_tokens: 最大token数
        enable_knowledge: 是否启用知识库
        enable_history: 是否启用对话历史
        max_history_turns: 最大历史轮数
    """
    name: str = "智能客服"
    description: str = "基于知识库的智能问答客服"
    agent_type: AgentType = AgentType.CUSTOMER_SERVICE
    system_prompt: str = ""
    model_id: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2000
    enable_knowledge: bool = True
    enable_history: bool = True
    max_history_turns: int = 5

    def get_system_prompt(self) -> str:
        """获取系统提示词，如果未设置则返回默认值"""
        if self.system_prompt:
            return self.system_prompt

        return f"""你是一个专业的{self.name}助手。

你的职责是：
1. 礼貌、专业地回答用户问题
2. 基于知识库内容提供准确信息
3. 如果不确定答案，诚实告知用户
4. 保持友好、耐心的服务态度

回答要求：
- 简洁明了，重点突出
- 使用用户能理解的语言
- 必要时提供分步骤说明
- 如果涉及专业术语，请适当解释
"""


@dataclass
class ChatResult:
    """
    聊天结果

    Attributes:
        success: 是否成功
        reply: 回复内容
        agent_used: 使用的Agent名称
        has_knowledge: 是否使用了知识库
        user_id: 用户ID
        session_id: 会话ID
        duration_ms: 处理耗时（毫秒）
        error: 错误信息
    """
    success: bool
    reply: str
    agent_used: str = ""
    has_knowledge: bool = False
    user_id: str = ""
    session_id: Optional[str] = None
    duration_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "reply": self.reply,
            "agent_used": self.agent_used,
            "has_knowledge": self.has_knowledge,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "duration_ms": self.duration_ms,
        }
        if self.error:
            result["error"] = self.error
        return result


class CustomerServiceAgent:
    """
    通用智能客服Agent

    特性：
    - 基于agno框架
    - 支持知识库增强（RAG）
    - 支持多轮对话
    - 可配置系统提示词
    - 企业级错误处理和日志

    Example:
        ```python
        # 创建Agent
        agent = CustomerServiceAgent()

        # 单轮对话
        result = await agent.chat("你好")

        # 多轮对话
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "您好！有什么可以帮您？"}
        ]
        result = await agent.chat("我想咨询一个问题", conversation_history=history)
        ```
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        llm_client=None,
        knowledge_base=None,
        prompt_name: str = "default"
    ):
        """
        初始化智能客服Agent

        Args:
            config: Agent配置，如果不提供则使用默认配置
            llm_client: 自定义LLM客户端（可选）
            knowledge_base: 知识库实例（可选，用于RAG）
            prompt_name: 提示词名称（从数据库读取）

        Raises:
            ImportError: 如果agno未安装
            ValueError: 如果配置无效
        """
        self.config = config or AgentConfig()
        self.knowledge_base = knowledge_base
        self.prompt_name = prompt_name
        self._agent = None
        self._llm_client = llm_client

        # 初始化知识库
        if self.knowledge_base is None:
            self._init_knowledge_base()

        # 初始化agno Agent
        self._init_agent()

        logger.info(f"✅ CustomerServiceAgent initialized: {self.config.name}")

    def _init_knowledge_base(self):
        """初始化知识库"""
        try:
            from common.knowledge_base import KnowledgeBase
            self.knowledge_base = KnowledgeBase()
            logger.info("✅ 知识库已初始化")
        except Exception as e:
            logger.warning(f"⚠️ 知识库初始化失败: {e}")
            self.knowledge_base = None

    def _init_agent(self):
        """初始化agno Agent"""
        try:
            from agno.agent import Agent

            # 创建LLM模型
            if self._llm_client:
                model = self._llm_client
            else:
                # 使用模型管理器从数据库获取配置
                from common.model_manager import model_manager
                model = model_manager.create_llm_model()

            # 从数据库获取系统提示词
            from common.prompt_manager import prompt_manager
            system_prompt = prompt_manager.get_system_prompt(self.prompt_name)
            logger.info(f"📝 使用提示词: {self.prompt_name}")

            # 创建agno Agent
            self._agent = Agent(
                name=self.config.name,
                model=model,
                description=self.config.description,
                instructions=[system_prompt],
                markdown=True,
            )

        except ImportError as e:
            logger.error(f"❌ agno未安装: {e}")
            raise ImportError("请安装agno: pip install agno") from e
        except Exception as e:
            logger.error(f"❌ Agent初始化失败: {e}")
            raise

    async def chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_knowledge_base: Optional[bool] = None
    ) -> ChatResult:
        """
        处理用户消息

        Args:
            message: 用户消息
            user_id: 用户ID
            session_id: 会话ID（可选，如果不提供则自动创建）
            conversation_history: 对话历史（可选，如果不提供则从数据库读取）
            use_knowledge_base: 是否使用知识库（可选，默认使用配置值）

        Returns:
            ChatResult对象
        """
        start_time = time.time()

        # 会话管理
        from common.conversation_manager import conversation_manager
        if not session_id:
            session_id = conversation_manager.create_session(user_id)

        # 获取对话历史（如果没有提供）
        if conversation_history is None and self.config.enable_history:
            conversation_history = conversation_manager.get_history(session_id)

        # 保存用户消息
        conversation_manager.save_message(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=message
        )

        # 确定是否使用知识库
        if use_knowledge_base is None:
            use_knowledge_base = self.config.enable_knowledge and self.knowledge_base is not None

        try:
            # 知识库检索
            knowledge_context = ""
            if use_knowledge_base and self.knowledge_base:
                knowledge_context = await self._retrieve_knowledge(message)

            # 构建完整的消息
            full_message = self._build_message(
                message,
                knowledge_context,
                conversation_history if self.config.enable_history else None
            )

            # 调用agno Agent
            response = await self._agent.arun(full_message)

            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)

            # 保存助手回复
            conversation_manager.save_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=response.content,
                agent_used=self.config.name,
                duration_ms=duration_ms
            )

            return ChatResult(
                success=True,
                reply=response.content,
                agent_used=self.config.name,
                has_knowledge=bool(knowledge_context),
                user_id=user_id,
                session_id=session_id,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Chat error: {e}", exc_info=True)

            return ChatResult(
                success=False,
                reply="抱歉，处理您的请求时出现错误，请稍后重试。",
                agent_used=self.config.name,
                user_id=user_id,
                session_id=session_id,
                duration_ms=duration_ms,
                error=str(e)
            )

    async def stream_chat(
        self,
        message: str,
        user_id: str = "default",
        session_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_knowledge_base: Optional[bool] = None
    ):
        """
        流式处理用户消息

        Args:
            message: 用户消息
            user_id: 用户ID
            session_id: 会话ID（可选）
            conversation_history: 对话历史（可选）
            use_knowledge_base: 是否使用知识库（可选）

        Yields:
            逐步生成的回复内容
        """
        start_time = time.time()

        # 会话管理
        from common.conversation_manager import conversation_manager
        if not session_id:
            session_id = conversation_manager.create_session(user_id)

        # 获取对话历史
        if conversation_history is None and self.config.enable_history:
            conversation_history = conversation_manager.get_history(session_id)

        # 保存用户消息
        conversation_manager.save_message(
            session_id=session_id,
            user_id=user_id,
            role="user",
            content=message
        )

        # 确定是否使用知识库
        if use_knowledge_base is None:
            use_knowledge_base = self.config.enable_knowledge and self.knowledge_base is not None

        try:
            # 知识库检索
            knowledge_context = ""
            if use_knowledge_base and self.knowledge_base:
                knowledge_context = await self._retrieve_knowledge(message)

            # 构建完整的消息
            full_message = self._build_message(
                message,
                knowledge_context,
                conversation_history if self.config.enable_history else None
            )

            # 流式调用agno Agent
            full_reply = ""
            async for chunk in self._agent.arun(full_message, stream=True):
                if chunk and hasattr(chunk, 'content') and chunk.content:
                    full_reply += chunk.content
                    yield {
                        "type": "chunk",
                        "content": chunk.content,
                        "session_id": session_id
                    }

            # 计算耗时
            duration_ms = int((time.time() - start_time) * 1000)

            # 保存助手回复
            conversation_manager.save_message(
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=full_reply,
                agent_used=self.config.name,
                duration_ms=duration_ms
            )

            # 发送完成信号
            yield {
                "type": "done",
                "session_id": session_id,
                "duration_ms": duration_ms,
                "full_reply": full_reply
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Stream chat error: {e}", exc_info=True)
            yield {
                "type": "error",
                "error": str(e),
                "session_id": session_id,
                "duration_ms": duration_ms
            }

    async def _retrieve_knowledge(self, query: str) -> str:
        """
        从知识库检索相关内容

        Args:
            query: 用户查询

        Returns:
            知识库上下文字符串
        """
        try:
            if hasattr(self.knowledge_base, 'search'):
                results = await self.knowledge_base.search(query, top_k=3)
                if results:
                    # SearchResult是dataclass，使用.content属性
                    context_parts = [r.content for r in results if hasattr(r, 'content') and r.content]
                    return "\n\n".join(context_parts)
            return ""
        except Exception as e:
            logger.warning(f"⚠️ Knowledge retrieval failed: {e}")
            return ""

    def _build_message(
        self,
        message: str,
        knowledge_context: str,
        conversation_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """
        构建完整的消息

        Args:
            message: 用户消息
            knowledge_context: 知识库上下文
            conversation_history: 对话历史

        Returns:
            构建后的完整消息
        """
        parts = []

        # 添加知识库上下文
        if knowledge_context:
            parts.append(f"【参考知识】\n{knowledge_context}\n")

        # 添加对话历史
        if conversation_history:
            recent_history = conversation_history[-self.config.max_history_turns:]
            history_text = "【对话历史】\n"
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                # 翻译角色名称
                role_name = "用户" if role == "user" else "助手"
                history_text += f"{role_name}: {content}\n"
            parts.append(history_text)

        # 添加当前问题
        parts.append(f"【用户问题】\n{message}")

        return "\n".join(parts)

    def update_system_prompt(self, new_prompt: str):
        """
        更新系统提示词

        Args:
            new_prompt: 新的系统提示词
        """
        self.config.system_prompt = new_prompt
        self._init_agent()
        logger.info(f"✅ System prompt updated for {self.config.name}")

    def get_info(self) -> Dict[str, Any]:
        """
        获取Agent信息

        Returns:
            Agent信息字典
        """
        # 从model_manager获取当前激活的模型信息
        from common.model_manager import model_manager
        model_info = model_manager.get_current_model_info()

        return {
            "name": self.config.name,
            "description": self.config.description,
            "type": self.config.agent_type.value,
            "model": model_info.get("model_id", self.config.model_id),
            "model_source": model_info.get("source", "default"),
            "model_name": model_info.get("name", "default"),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "enable_knowledge": self.config.enable_knowledge,
            "enable_history": self.config.enable_history,
            "has_knowledge_base": self.knowledge_base is not None,
        }
