"""
模型管理器 - 从数据库读取和管理LLM模型配置

支持：
- 从数据库读取激活的模型配置
- 创建LLM模型实例
- 动态切换模型
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """模型配置"""
    id: int
    name: str
    provider: str
    model_id: str
    base_url: str
    api_key: str
    parameters: Dict[str, Any]


class ModelManager:
    """
    模型管理器

    从数据库读取模型配置，创建LLM模型实例。
    """

    _instance = None
    _current_model = None
    _current_config = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_active_model_config(self) -> Optional[ModelConfig]:
        """
        获取激活的模型配置

        Returns:
            模型配置，如果没有激活的模型则返回None
        """
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, provider, model_id, base_url, api_key_encrypted, parameters
                    FROM ai_service.model_configs
                    WHERE is_active = TRUE
                    LIMIT 1
                    """
                )
                result = cursor.fetchone()

                if result:
                    return ModelConfig(
                        id=result['id'],
                        name=result['name'],
                        provider=result['provider'],
                        model_id=result['model_id'],
                        base_url=result.get('base_url', ''),
                        api_key=result.get('api_key_encrypted', ''),
                        parameters=result.get('parameters', {})
                    )
                return None

        except Exception as e:
            logger.warning(f"⚠️ 从数据库获取模型配置失败: {e}")
            return None

    def create_llm_model(self, config: Optional[ModelConfig] = None):
        """
        创建LLM模型实例

        Args:
            config: 模型配置，如果不提供则使用激活的模型

        Returns:
            LLM模型实例
        """
        try:
            from agno.models.openai import OpenAIChat

            # 获取配置
            if config is None:
                config = self.get_active_model_config()

            # 如果没有数据库配置，使用默认配置
            if config is None:
                logger.info("📝 使用默认模型配置")
                return OpenAIChat(
                    id="gpt-4o-mini",
                    temperature=0.7,
                    max_tokens=2000
                )

            # 从配置创建模型
            base_url = config.base_url or "https://api.openai.com/v1"
            api_key = config.api_key or ""
            temperature = config.parameters.get('temperature', 0.7)
            max_tokens = config.parameters.get('max_tokens', 2000)

            logger.info(f"✅ 创建模型: {config.name} ({config.model_id})")

            model = OpenAIChat(
                id=config.model_id,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 设置role映射，将developer映射为system（兼容大多数API）
            model.default_role_map = {
                "system": "system",
                "user": "user",
                "assistant": "assistant",
                "tool": "tool",
                "model": "assistant",
            }

            return model

        except Exception as e:
            logger.error(f"❌ 创建模型失败: {e}")
            # 返回默认模型
            from agno.models.openai import OpenAIChat
            return OpenAIChat(id="gpt-4o-mini")

    def get_current_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息

        Returns:
            模型信息字典
        """
        config = self.get_active_model_config()

        if config:
            return {
                "source": "database",
                "id": config.id,
                "name": config.name,
                "provider": config.provider,
                "model_id": config.model_id,
                "base_url": config.base_url
            }
        else:
            return {
                "source": "config_file",
                "name": "默认模型",
                "model_id": "gpt-4o-mini"
            }

    def clear_cache(self):
        """清除缓存，下次获取时重新从数据库读取"""
        self._current_model = None
        self._current_config = None
        logger.info("✅ 模型缓存已清除")


# 全局实例
model_manager = ModelManager()
