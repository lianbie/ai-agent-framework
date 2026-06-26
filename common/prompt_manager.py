"""
提示词管理器 - 从数据库读取和管理Agent提示词

支持：
- 从数据库读取提示词
- 缓存提示词（Redis）
- 动态切换提示词
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class PromptManager:
    """
    提示词管理器

    从数据库读取提示词配置。
    """

    _instance = None
    _cache = {}

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_prompt(self, prompt_name: str = "default") -> Optional[Dict[str, Any]]:
        """
        获取提示词配置

        Args:
            prompt_name: 提示词名称

        Returns:
            提示词配置字典
        """
        # 检查缓存
        if prompt_name in self._cache:
            return self._cache[prompt_name]

        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                # 优先获取指定名称的提示词
                cursor.execute(
                    """
                    SELECT id, name, system_prompt, variables
                    FROM ai_service.prompts
                    WHERE name = %s AND is_default = FALSE
                    LIMIT 1
                    """,
                    (prompt_name,)
                )
                result = cursor.fetchone()

                # 如果没有找到，获取默认提示词
                if not result:
                    cursor.execute(
                        """
                        SELECT id, name, system_prompt, variables
                        FROM ai_service.prompts
                        WHERE is_default = TRUE
                        LIMIT 1
                        """
                    )
                    result = cursor.fetchone()

                if result:
                    prompt_config = {
                        "id": result['id'],
                        "name": result['name'],
                        "system_prompt": result['system_prompt'],
                        "variables": result.get('variables', {})
                    }
                    # 缓存
                    self._cache[prompt_name] = prompt_config
                    return prompt_config

                return None

        except Exception as e:
            logger.warning(f"⚠️ 从数据库获取提示词失败: {e}")
            return None

    def get_system_prompt(self, prompt_name: str = "default") -> str:
        """
        获取系统提示词文本

        Args:
            prompt_name: 提示词名称

        Returns:
            系统提示词文本
        """
        config = self.get_prompt(prompt_name)

        if config and config.get('system_prompt'):
            return config['system_prompt']

        # 返回默认提示词
        return """你是一个专业的智能客服助手。

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

    def clear_cache(self, prompt_name: Optional[str] = None):
        """
        清除缓存

        Args:
            prompt_name: 指定清除的提示词名称，None则清除所有
        """
        if prompt_name:
            self._cache.pop(prompt_name, None)
        else:
            self._cache.clear()
        logger.info("✅ 提示词缓存已清除")

    def get_all_prompts(self):
        """获取所有提示词列表"""
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, description, is_default, version
                    FROM ai_service.prompts
                    ORDER BY is_default DESC, created_at DESC
                    """
                )
                return cursor.fetchall()

        except Exception as e:
            logger.error(f"❌ 获取提示词列表失败: {e}")
            return []


# 全局实例
prompt_manager = PromptManager()
