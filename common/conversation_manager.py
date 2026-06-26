"""
对话历史管理器 - 存储和管理对话历史

支持：
- 存储对话历史到数据库
- 获取对话历史
- 多会话管理
"""

import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    对话历史管理器

    将对话历史持久化到PostgreSQL数据库。
    """

    _instance = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_session(self, user_id: str = "default") -> str:
        """
        创建新会话

        Args:
            user_id: 用户ID

        Returns:
            会话ID
        """
        session_id = f"session_{uuid.uuid4().hex[:16]}"
        logger.info(f"✅ 创建会话: {session_id}")
        return session_id

    def save_message(
        self,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        agent_used: str = "",
        model_id: str = "",
        duration_ms: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        保存对话消息

        Args:
            session_id: 会话ID
            user_id: 用户ID
            role: 角色 (user/assistant)
            content: 消息内容
            agent_used: 使用的Agent名称
            model_id: 使用的模型ID
            duration_ms: 处理耗时
            metadata: 额外元数据

        Returns:
            是否保存成功
        """
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ai_service.conversations
                    (session_id, user_id, role, content, agent_used, model_id, duration_ms, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        user_id,
                        role,
                        content,
                        agent_used,
                        model_id,
                        duration_ms,
                        '{}'
                    )
                )

            logger.debug(f"💾 保存消息: {role} - {content[:50]}...")
            return True

        except Exception as e:
            logger.error(f"❌ 保存消息失败: {e}")
            return False

    def get_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        获取对话历史

        Args:
            session_id: 会话ID
            limit: 返回条数

        Returns:
            对话历史列表
        """
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT role, content, created_at
                    FROM ai_service.conversations
                    WHERE session_id = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                    """,
                    (session_id, limit)
                )
                results = cursor.fetchall()

                return [
                    {
                        "role": row['role'],
                        "content": row['content'],
                        "created_at": row['created_at'].isoformat() if row['created_at'] else None
                    }
                    for row in results
                ]

        except Exception as e:
            logger.error(f"❌ 获取对话历史失败: {e}")
            return []

    def get_user_sessions(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取用户的会话列表

        Args:
            user_id: 用户ID
            limit: 返回条数

        Returns:
            会话列表
        """
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        session_id,
                        COUNT(*) as message_count,
                        MIN(created_at) as started_at,
                        MAX(created_at) as last_message_at,
                        (SELECT content FROM ai_service.conversations c2
                         WHERE c2.session_id = c.session_id
                         ORDER BY c2.created_at DESC LIMIT 1) as last_message
                    FROM ai_service.conversations c
                    WHERE user_id = %s
                    GROUP BY session_id
                    ORDER BY last_message_at DESC
                    LIMIT %s
                    """,
                    (user_id, limit)
                )
                results = cursor.fetchall()

                return [
                    {
                        "session_id": row['session_id'],
                        "message_count": row['message_count'],
                        "started_at": row['started_at'].isoformat() if row['started_at'] else None,
                        "last_message_at": row['last_message_at'].isoformat() if row['last_message_at'] else None,
                        "last_message": row['last_message']
                    }
                    for row in results
                ]

        except Exception as e:
            logger.error(f"❌ 获取会话列表失败: {e}")
            return []

    def delete_session(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否删除成功
        """
        try:
            from common.postgresql_pool import pg_pool

            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    "DELETE FROM ai_service.conversations WHERE session_id = %s",
                    (session_id,)
                )

            logger.info(f"✅ 删除会话: {session_id}")
            return True

        except Exception as e:
            logger.error(f"❌ 删除会话失败: {e}")
            return False


# 全局实例
conversation_manager = ConversationManager()
