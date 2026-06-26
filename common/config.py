"""
配置管理模块

提供统一的配置加载和管理。
企业级设计：支持多环境配置、配置验证、环境变量覆盖。

Usage:
    from common.config import config

    # 获取配置
    db_host = config.get("postgresql.host")
    api_key = config.get("llm_server.api_key")

    # 获取整个配置节
    pg_config = config.get_section("postgresql")
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Config:
    """
    配置管理类

    支持：
    - 从JSON文件加载配置
    - 环境变量覆盖
    - 点分隔的配置路径
    - 配置验证

    Example:
        ```python
        from common.config import config

        # 获取配置
        db_host = config.get("postgresql.host")
        api_key = config.get("llm_server.api_key", default="")

        # 获取整个配置节
        pg_config = config.get_section("postgresql")
        ```
    """

    def __init__(self, config_path: str = "config.json"):
        """
        初始化配置管理器

        Args:
            config_path: 配置文件路径
        """
        self._config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        config_path = Path(self._config_path)

        if not config_path.exists():
            logger.warning(f"⚠️ Config file not found: {self._config_path}")
            self._config = {}
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info(f"✅ Config loaded: {self._config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in config file: {e}")
            self._config = {}
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            self._config = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        支持点分隔的配置路径，例如：
        - config.get("postgresql.host")
        - config.get("llm_server.api_key")

        Args:
            key: 配置键（支持点分隔路径）
            default: 默认值

        Returns:
            配置值
        """
        # 检查环境变量覆盖
        env_key = key.replace(".", "_").upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value

        # 从配置文件获取
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取整个配置节

        Args:
            section: 配置节名称

        Returns:
            配置节字典
        """
        return self._config.get(section, {})

    def set(self, key: str, value: Any):
        """
        设置配置值（运行时）

        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def reload(self):
        """重新加载配置文件"""
        self._load_config()

    def to_dict(self) -> Dict[str, Any]:
        """
        导出配置为字典

        Returns:
            配置字典
        """
        return self._config.copy()

    def validate(self, required_keys: list) -> bool:
        """
        验证必需的配置项是否存在

        Args:
            required_keys: 必需的配置键列表

        Returns:
            是否所有必需配置都存在
        """
        missing_keys = []

        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)

        if missing_keys:
            logger.warning(f"⚠️ Missing required config keys: {missing_keys}")
            return False

        return True


# 创建全局配置实例
config = Config()


# 向后兼容的别名
server_config = config


def load_server_config() -> Dict[str, Any]:
    """
    加载服务器配置（向后兼容）

    Returns:
        配置字典
    """
    return config.to_dict()
