"""
对话管理API
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
import logging
import csv
import io
from datetime import datetime

from common.postgresql_pool import pg_pool
from modules.admin_api.models import ConversationResponse, ConversationExportRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["对话管理"])


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    page: int = 1,
    page_size: int = 50,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    role: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    获取对话历史

    - **page**: 页码
    - **page_size**: 每页数量
    - **session_id**: 会话ID过滤
    - **user_id**: 用户ID过滤
    - **role**: 角色过滤 (user, assistant)
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            query = "SELECT * FROM ai_service.conversations"
            params = []
            conditions = []

            if session_id:
                conditions.append("session_id = %s")
                params.append(session_id)

            if user_id:
                conditions.append("user_id = %s")
                params.append(user_id)

            if role:
                conditions.append("role = %s")
                params.append(role)

            if start_date:
                conditions.append("created_at >= %s")
                params.append(start_date)

            if end_date:
                conditions.append("created_at <= %s")
                params.append(end_date)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [ConversationResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取对话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[dict])
async def list_sessions(
    page: int = 1,
    page_size: int = 20
):
    """
    获取会话列表

    - **page**: 页码
    - **page_size**: 每页数量
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    session_id,
                    user_id,
                    COUNT(*) as message_count,
                    MIN(created_at) as started_at,
                    MAX(created_at) as last_message_at
                FROM ai_service.conversations
                GROUP BY session_id, user_id
                ORDER BY last_message_at DESC
                LIMIT %s OFFSET %s
                """,
                (page_size, (page - 1) * page_size)
            )
            results = cursor.fetchall()

            return results

    except Exception as e:
        logger.error(f"❌ 获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=List[ConversationResponse])
async def get_session(session_id: str):
    """
    获取会话详情

    - **session_id**: 会话ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM ai_service.conversations
                WHERE session_id = %s
                ORDER BY created_at ASC
                """,
                (session_id,)
            )
            results = cursor.fetchall()

            return [ConversationResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取会话详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """
    删除单条对话

    - **conversation_id**: 对话ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "DELETE FROM ai_service.conversations WHERE id = %s",
                (conversation_id,)
            )

            return {"success": True, "message": "对话已删除"}

    except Exception as e:
        logger.error(f"❌ 删除对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    删除整个会话

    - **session_id**: 会话ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "DELETE FROM ai_service.conversations WHERE session_id = %s",
                (session_id,)
            )

            return {"success": True, "message": "会话已删除"}

    except Exception as e:
        logger.error(f"❌ 删除会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_conversations(request: ConversationExportRequest):
    """
    导出对话

    - **session_id**: 会话ID（可选）
    - **user_id**: 用户ID（可选）
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    - **format**: 导出格式 (json, csv)
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            query = "SELECT * FROM ai_service.conversations"
            params = []
            conditions = []

            if request.session_id:
                conditions.append("session_id = %s")
                params.append(request.session_id)

            if request.user_id:
                conditions.append("user_id = %s")
                params.append(request.user_id)

            if request.start_date:
                conditions.append("created_at >= %s")
                params.append(request.start_date)

            if request.end_date:
                conditions.append("created_at <= %s")
                params.append(request.end_date)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at ASC"

            cursor.execute(query, params)
            results = cursor.fetchall()

            if request.format == "csv":
                # CSV格式
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["id", "session_id", "user_id", "role", "content", "created_at"])

                for row in results:
                    writer.writerow([
                        row['id'], row['session_id'], row['user_id'],
                        row['role'], row['content'], row['created_at']
                    ])

                output.seek(0)
                return StreamingResponse(
                    iter([output.getvalue()]),
                    media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=conversations.csv"}
                )
            else:
                # JSON格式
                return results

    except Exception as e:
        logger.error(f"❌ 导出对话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
