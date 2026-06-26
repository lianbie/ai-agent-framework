"""
PostgreSQL连接池管理

提供企业级的PostgreSQL连接池管理。
支持连接健康检查、自动重连、事务管理。

Usage:
    from common.postgresql_pool import pg_pool

    # 使用上下文管理器
    with pg_pool.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()

    # 使用字典游标
    with pg_pool.get_dict_cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
"""

import psycopg2
import psycopg2.extras
from psycopg2 import pool
from contextlib import contextmanager
from typing import Optional, Dict, Any
import logging

from common.config import config

logger = logging.getLogger(__name__)


class PostgreSQLPool:
    """
    PostgreSQL连接池管理类

    特性：
    - 线程安全的连接池
    - 连接健康检查
    - 自动重连机制
    - 事务管理
    - pgvector支持

    Example:
        ```python
        from common.postgresql_pool import pg_pool

        # 基础用法
        with pg_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                results = cursor.fetchall()

        # 字典游标
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            for row in cursor.fetchall():
                print(row['name'])
        ```
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "postgresql.default"):
        """
        初始化连接池

        Args:
            config_path: 配置路径（默认从config.json读取）
        """
        if hasattr(self, '_initialized'):
            return

        self._config_path = config_path
        self._pool = None
        self._init_pool()
        self._initialized = True

    def _get_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        pg_config = config.get_section("postgresql")
        return pg_config.get("default", {
            "host": "localhost",
            "port": 5432,
            "database": "ai_service",
            "user": "postgres",
            "password": ""
        })

    def _init_pool(self):
        """初始化连接池"""
        try:
            db_config = self._get_config()

            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=20,
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 5432),
                database=db_config.get('database', 'ai_service'),
                user=db_config.get('user', 'postgres'),
                password=db_config.get('password', ''),
                cursor_factory=psycopg2.extras.RealDictCursor,
                # 连接保活参数
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )

            logger.info("✅ PostgreSQL连接池初始化成功")

        except Exception as e:
            logger.error(f"❌ PostgreSQL连接池初始化失败: {e}")
            raise

    def _check_connection_health(self, conn) -> bool:
        """
        检查连接健康状态

        Args:
            conn: 数据库连接

        Returns:
            连接是否健康
        """
        try:
            return conn.closed == 0
        except Exception:
            return False

    @contextmanager
    def get_connection(self):
        """
        获取数据库连接的上下文管理器

        自动处理连接获取、健康检查、事务提交和回滚。

        Yields:
            数据库连接

        Example:
            ```python
            with pg_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO users (name) VALUES (%s)", ("test",))
                conn.commit()
            ```
        """
        conn = None
        max_retries = 3
        retry_count = 0

        try:
            while retry_count < max_retries:
                try:
                    conn = self._pool.getconn()

                    # 检查连接健康状态
                    if not self._check_connection_health(conn):
                        logger.warning(f"⚠️ 连接不健康，重试 ({retry_count + 1}/{max_retries})")
                        self._pool.putconn(conn, close=True)
                        retry_count += 1
                        conn = None
                        continue

                    # 清理未完成的事务
                    try:
                        conn.rollback()
                    except Exception:
                        pass

                    yield conn
                    return

                except psycopg2.OperationalError as e:
                    logger.error(f"❌ 数据库连接错误: {e}")
                    if conn:
                        try:
                            self._pool.putconn(conn, close=True)
                        except Exception:
                            pass
                        conn = None
                    retry_count += 1

                    if retry_count >= max_retries:
                        raise

            raise psycopg2.OperationalError("无法获取数据库连接")

        except Exception as e:
            # 回滚事务
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            raise

        finally:
            # 归还连接到连接池
            if conn:
                try:
                    self._pool.putconn(conn)
                except Exception:
                    pass

    @contextmanager
    def get_dict_cursor(self, auto_commit: bool = True):
        """
        获取字典游标的上下文管理器

        Args:
            auto_commit: 是否自动提交事务（默认True）

        Yields:
            字典游标

        Example:
            ```python
            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute("SELECT * FROM users")
                for row in cursor.fetchall():
                    print(row['name'])
            ```
        """
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                try:
                    yield cursor
                    if auto_commit:
                        conn.commit()
                except Exception:
                    conn.rollback()
                    raise

    def close(self):
        """关闭连接池"""
        if self._pool:
            self._pool.closeall()
            logger.info("✅ PostgreSQL连接池已关闭")

    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接池统计信息

        Returns:
            统计信息字典
        """
        if not self._pool:
            return {"status": "not_initialized"}

        return {
            "status": "active",
            "min_connections": self._pool.minconn,
            "max_connections": self._pool.maxconn,
        }


# 创建全局连接池实例
pg_pool = PostgreSQLPool()
