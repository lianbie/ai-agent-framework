"""
管理后台数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============ 枚举类型 ============

class DocumentStatus(str, Enum):
    """文档状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# ============ 提示词模型 ============

class PromptBase(BaseModel):
    """提示词基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="提示词名称")
    description: Optional[str] = Field(None, description="描述")
    system_prompt: str = Field(..., min_length=1, description="系统提示词")
    variables: Optional[Dict[str, Any]] = Field(default={}, description="模板变量")
    is_default: bool = Field(default=False, description="是否默认")


class PromptCreate(PromptBase):
    """创建提示词"""
    pass


class PromptUpdate(BaseModel):
    """更新提示词"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=1)
    variables: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None


class PromptResponse(PromptBase):
    """提示词响应"""
    id: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PromptTestRequest(BaseModel):
    """提示词测试请求"""
    prompt_id: int
    message: str = Field(..., min_length=1, description="测试消息")
    variables: Optional[Dict[str, str]] = Field(default={}, description="变量值")


# ============ 知识库模型 ============

class DocumentResponse(BaseModel):
    """文档响应"""
    id: int
    filename: str
    file_type: Optional[str]
    file_size: Optional[int]
    chunk_count: int
    status: DocumentStatus
    error_message: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeSearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str = Field(..., min_length=1, description="搜索内容")
    top_k: int = Field(default=5, ge=1, le=20, description="返回数量")


class KnowledgeSearchResult(BaseModel):
    """搜索结果"""
    content: str
    score: float
    metadata: Dict[str, Any]


class KnowledgeStats(BaseModel):
    """知识库统计"""
    total_documents: int
    completed_documents: int
    total_chunks: int
    total_size_bytes: int


# ============ 模型配置模型 ============

class ModelConfigBase(BaseModel):
    """模型配置基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="模型名称")
    provider: str = Field(..., description="提供商")
    model_id: str = Field(..., description="模型ID")
    base_url: Optional[str] = Field(None, description="API地址")
    api_key: Optional[str] = Field(None, description="API密钥")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="模型参数")


class ModelConfigCreate(ModelConfigBase):
    """创建模型配置"""
    pass


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = None
    model_id: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    id: int
    name: str
    provider: str
    model_id: str
    base_url: Optional[str]
    parameters: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelTestRequest(BaseModel):
    """模型测试请求"""
    model_id: int
    message: str = Field(default="你好，请介绍一下自己", description="测试消息")


# ============ 对话模型 ============

class ConversationResponse(BaseModel):
    """对话响应"""
    id: int
    session_id: str
    user_id: Optional[str]
    role: str
    content: str
    agent_used: Optional[str]
    prompt_id: Optional[int]
    model_id: Optional[str]
    tokens_used: int
    duration_ms: int
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationExportRequest(BaseModel):
    """对话导出请求"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    format: str = Field(default="json", description="导出格式: json, csv")


# ============ 系统监控模型 ============

class SystemStats(BaseModel):
    """系统统计"""
    total_conversations: int
    total_documents: int
    total_prompts: int
    total_models: int
    api_calls_today: int
    avg_response_time_ms: float
    error_rate: float


class SystemLog(BaseModel):
    """系统日志"""
    id: int
    level: LogLevel
    module: Optional[str]
    message: Optional[str]
    details: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """健康检查"""
    status: str
    version: str
    uptime_seconds: int
    database: bool
    redis: bool
    vector_store: bool


# ============ 通用模型 ============

class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class ApiResponse(BaseModel):
    """通用API响应"""
    success: bool
    message: str
    data: Optional[Any] = None
