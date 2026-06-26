"""
知识库管理API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

from common.postgresql_pool import pg_pool
from common.knowledge_base import KnowledgeBase
from modules.admin_api.models import (
    DocumentResponse, KnowledgeSearchRequest, KnowledgeSearchResult,
    KnowledgeStats, ApiResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["知识库管理"])

# 上传目录
UPLOAD_DIR = "uploads/knowledge"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_knowledge_base():
    """获取知识库实例"""
    return KnowledgeBase()


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None
):
    """
    获取文档列表

    - **page**: 页码
    - **page_size**: 每页数量
    - **status**: 状态过滤 (pending, processing, completed, failed)
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            query = "SELECT * FROM ai_service.knowledge_documents"
            params = []

            if status:
                query += " WHERE status = %s"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([page_size, (page - 1) * page_size])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [DocumentResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"❌ 获取文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    上传文档

    - **file**: 文档文件 (支持 txt, pdf, docx, xlsx)
    """
    try:
        # 检查文件类型
        allowed_types = ['.txt', '.pdf', '.docx', '.xlsx', '.csv', '.json']
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}，支持: {', '.join(allowed_types)}"
            )

        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # 保存文件
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        file_size = len(content)

        # 创建文档记录
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ai_service.knowledge_documents
                (filename, file_type, file_size, status, metadata)
                VALUES (%s, %s, %s, 'pending', %s)
                RETURNING *
                """,
                (file.filename, file_ext, file_size, '{"file_path": "' + file_path + '"}')
            )
            doc = cursor.fetchone()

        # 后台处理文档向量化
        background_tasks.add_task(process_document, doc['id'], file_path)

        return DocumentResponse(**doc)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_document(doc_id: int, file_path: str):
    """
    后台处理文档（向量化）

    Args:
        doc_id: 文档ID
        file_path: 文件路径
    """
    try:
        # 更新状态为处理中
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                "UPDATE ai_service.knowledge_documents SET status = 'processing' WHERE id = %s",
                (doc_id,)
            )

        # 获取知识库实例
        kb = get_knowledge_base()

        # 添加文档到知识库
        success = await kb.add_document(file_path)

        if success:
            # 更新状态为完成
            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE ai_service.knowledge_documents
                    SET status = 'completed', chunk_count = 1
                    WHERE id = %s
                    """,
                    (doc_id,)
                )
            logger.info(f"✅ 文档处理完成: {doc_id}")
        else:
            # 更新状态为失败
            with pg_pool.get_dict_cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE ai_service.knowledge_documents
                    SET status = 'failed', error_message = '处理失败'
                    WHERE id = %s
                    """,
                    (doc_id,)
                )
            logger.error(f"❌ 文档处理失败: {doc_id}")

    except Exception as e:
        logger.error(f"❌ 文档处理异常: {e}")
        with pg_pool.get_dict_cursor() as cursor:
            cursor.execute(
                """
                UPDATE ai_service.knowledge_documents
                SET status = 'failed', error_message = %s
                WHERE id = %s
                """,
                (str(e), doc_id)
            )


@router.delete("/documents/{doc_id}", response_model=ApiResponse)
async def delete_document(doc_id: int):
    """
    删除文档

    - **doc_id**: 文档ID
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 获取文档信息
            cursor.execute(
                "SELECT * FROM ai_service.knowledge_documents WHERE id = %s",
                (doc_id,)
            )
            doc = cursor.fetchone()

            if not doc:
                raise HTTPException(status_code=404, detail="文档不存在")

            # 删除文件
            file_path = doc.get('metadata', {}).get('file_path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            # 删除记录
            cursor.execute(
                "DELETE FROM ai_service.knowledge_documents WHERE id = %s",
                (doc_id,)
            )

            return ApiResponse(success=True, message="文档已删除")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 删除文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[KnowledgeSearchResult])
async def search_knowledge(request: KnowledgeSearchRequest):
    """
    搜索知识库

    - **query**: 搜索内容
    - **top_k**: 返回数量
    """
    try:
        kb = get_knowledge_base()
        results = await kb.search(request.query, top_k=request.top_k)

        return [
            KnowledgeSearchResult(
                content=r.content,
                score=r.score,
                metadata=r.metadata
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"❌ 搜索知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=KnowledgeStats)
async def get_stats():
    """
    获取知识库统计
    """
    try:
        with pg_pool.get_dict_cursor() as cursor:
            # 总文档数
            cursor.execute("SELECT COUNT(*) as total FROM ai_service.knowledge_documents")
            total = cursor.fetchone()['total']

            # 完成文档数
            cursor.execute(
                "SELECT COUNT(*) as completed FROM ai_service.knowledge_documents WHERE status = 'completed'"
            )
            completed = cursor.fetchone()['completed']

            # 总chunk数
            cursor.execute(
                "SELECT COALESCE(SUM(chunk_count), 0) as total_chunks FROM ai_service.knowledge_documents"
            )
            total_chunks = cursor.fetchone()['total_chunks']

            # 总大小
            cursor.execute(
                "SELECT COALESCE(SUM(file_size), 0) as total_size FROM ai_service.knowledge_documents"
            )
            total_size = cursor.fetchone()['total_size']

            return KnowledgeStats(
                total_documents=total,
                completed_documents=completed,
                total_chunks=total_chunks,
                total_size_bytes=total_size
            )

    except Exception as e:
        logger.error(f"❌ 获取知识库统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
