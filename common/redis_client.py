"""
Redis客户端模块

提供企业级的Redis客户端封装。
支持连接池、自动序列化、缓存装饰器。

Usage:
    from common.redis_client import redis_client

    # 基础操作
    redis_client.set("key", "value", ex=3600)
    value = redis_client.get("key")

    # 缓存装饰器
    @redis_client.cache(ttl=3600)
    def get_user(user_id):
        return db.query(user_id)
"""

import redis
import json
import functools
from typing import Optional, Any, Callable
import logging

from common.config import config

logger = logging.getLogger(__name__)


class RedisClient:
    """
    Redis客户端封装类

    特性：
    - 连接池管理
    - 自动序列化/反序列化
    - 缓存装饰器
    - 健康检查

    Example:
        ```python
        from common.redis_client import redis_client

        # 基础操作
        redis_client.set("user:123", {"name": "test"}, ex=3600)
        user = redis_client.get("user:123")

        # 缓存装饰器
        @redis_client.cache(ttl=300)
        def get_data(id):
            return expensive_query(id)
        ```
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化Redis客户端"""
        if hasattr(self, '_initialized'):
            return

        self._redis = None
        self._init_client()
        self._initialized = True

    def _get_config(self) -> dict:
        """获取Redis配置"""
        return config.get_section("redis") or {
            "host": "127.0.0.1",
            "port": 6379,
            "password": None,
            "db": 0
        }

    def _init_client(self):
        """初始化Redis客户端"""
        try:
            redis_config = self._get_config()

            pool = redis.ConnectionPool(
                host=redis_config.get('host', '127.0.0.1'),
                port=redis_config.get('port', 6379),
                password=redis_config.get('password'),
                db=redis_config.get('db', 0),
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=False,
                max_connections=20
            )

            self._redis = redis.Redis(connection_pool=pool)
            logger.info("✅ Redis客户端初始化成功")

        except Exception as e:
            logger.warning(f"⚠️ Redis客户端初始化失败: {e}")
            self._redis = None

    def _serialize(self, value: Any) -> str:
        """
        序列化值

        Args:
            value: 要序列化的值

        Returns:
            序列化后的字符串
        """
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value, ensure_ascii=False)

    def _deserialize(self, value: str) -> Any:
        """
        反序列化值

        Args:
            value: 要反序列化的字符串

        Returns:
            反序列化后的值
        """
        if value is None:
            return None

        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return value

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        设置键值对

        Args:
            key: 键
            value: 值
            ex: 过期时间（秒）

        Returns:
            是否成功
        """
        if not self._redis:
            logger.warning("⚠️ Redis未连接")
            return False

        try:
            serialized = self._serialize(value)
            return self._redis.set(key, serialized, ex=ex)
        except Exception as e:
            logger.error(f"❌ Redis SET failed: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取键值

        Args:
            key: 键
            default: 默认值

        Returns:
            键对应的值
        """
        if not self._redis:
            logger.warning("⚠️ Redis未连接")
            return default

        try:
            value = self._redis.get(key)
            if value is None:
                return default
            return self._deserialize(value)
        except Exception as e:
            logger.error(f"❌ Redis GET failed: {e}")
            return default

    def delete(self, *keys) -> int:
        """
        删除键

        Args:
            keys: 键列表

        Returns:
            删除的键数量
        """
        if not self._redis:
            logger.warning("⚠️ Redis未连接")
            return 0

        try:
            return self._redis.delete(*keys)
        except Exception as e:
            logger.error(f"❌ Redis DELETE failed: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 键

        Returns:
            键是否存在
        """
        if not self._redis:
            return False

        try:
            return bool(self._redis.exists(key))
        except Exception as e:
            logger.error(f"❌ Redis EXISTS failed: {e}")
            return False

    def expire(self, key: str, seconds: int) -> bool:
        """
        设置过期时间

        Args:
            key: 键
            seconds: 过期时间（秒）

        Returns:
            是否成功
        """
        if not self._redis:
            return False

        try:
            return self._redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"❌ Redis EXPIRE failed: {e}")
            return False

    def keys(self, pattern: str = "*") -> list:
        """
        获取匹配的键

        Args:
            pattern: 匹配模式

        Returns:
            键列表
        """
        if not self._redis:
            return []

        try:
            return self._redis.keys(pattern)
        except Exception as e:
            logger.error(f"❌ Redis KEYS failed: {e}")
            return []

    def cache(self, ttl: int = 300, prefix: str = "cache"):
        """
        缓存装饰器

        Args:
            ttl: 缓存过期时间（秒）
            prefix: 缓存键前缀

        Returns:
            装饰器函数

        Example:
            ```python
            @redis_client.cache(ttl=3600)
            def get_user(user_id):
                return db.query(user_id)
            ```
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # 生成缓存键
                key_parts = [prefix, func.__name__] + [str(arg) for arg in args]
                key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
                cache_key = ":".join(key_parts)

                # 尝试从缓存获取
                cached = self.get(cache_key)
                if cached is not None:
                    return cached

                # 执行函数
                result = func(*args, **kwargs)

                # 缓存结果
                if result is not None:
                    self.set(cache_key, result, ex=ttl)

                return result
            return wrapper
        return decorator

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            Redis是否可用
        """
        if not self._redis:
            return False

        try:
            return self._redis.ping()
        except Exception:
            return False

    def close(self):
        """关闭连接"""
        if self._redis:
            try:
                self._redis.close()
                logger.info("✅ Redis连接已关闭")
            except Exception:
                pass


# 创建全局Redis客户端实例
redis_client = RedisClient()
