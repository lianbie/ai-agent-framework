# 🏗️ 架构设计文档

本文档描述了AI智能客服框架的架构设计。

## 系统概览

这是一个基于agno框架的通用智能客服服务，采用模块化设计，支持知识库增强问答、多会话管理、对话持久化。

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
├─────────────────────────────────────────────────────────┤
│                  /api/agent/chat                         │
├─────────────────────────────────────────────────────────┤
│              CustomerServiceAgent (agno)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. 接收用户消息                                  │   │
│  │  2. 会话管理（创建/获取会话）                    │   │
│  │  3. 获取对话历史                                  │   │
│  │  4. 检索知识库（如果启用）                        │   │
│  │  5. 构建增强Prompt                               │   │
│  │  6. 调用LLM生成回复                              │   │
│  │  7. 保存对话历史                                  │   │
│  │  8. 返回结构化响应                                │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL + pgvector  │  Redis  │  LangChain          │
└─────────────────────────────────────────────────────────┘
```

## 模块设计

### 1. CustomerServiceAgent

核心Agent类，基于agno框架：

```python
class CustomerServiceAgent:
    """
    特性：
    - 基于agno框架
    - 支持知识库增强（RAG）
    - 支持多轮对话
    - 支持会话管理
    - 对话历史持久化
    - 可配置系统提示词
    - 可切换LLM模型
    """
```

**主要方法：**
- `chat()` - 处理用户消息（自动管理会话和历史）
- `_retrieve_knowledge()` - 知识库检索
- `_build_message()` - 构建增强Prompt
- `_init_knowledge_base()` - 初始化知识库
- `_init_agent()` - 初始化agno Agent

### 2. ModelManager - 模型管理器

从数据库读取和管理LLM模型配置：

```python
class ModelManager:
    """
    特性：
    - 从数据库读取激活的模型配置
    - 创建LLM模型实例
    - 动态切换模型
    - 角色映射兼容
    """
```

**主要方法：**
- `get_active_model_config()` - 获取激活的模型配置
- `create_llm_model()` - 创建LLM模型实例
- `get_current_model_info()` - 获取当前模型信息
- `clear_cache()` - 清除缓存

### 3. PromptManager - 提示词管理器

从数据库读取和管理提示词：

```python
class PromptManager:
    """
    特性：
    - 从数据库读取提示词
    - 缓存提示词
    - 动态切换提示词
    """
```

**主要方法：**
- `get_prompt()` - 获取提示词配置
- `get_system_prompt()` - 获取系统提示词文本
- `clear_cache()` - 清除缓存

### 4. ConversationManager - 对话管理器

管理对话历史和会话：

```python
class ConversationManager:
    """
    特性：
    - 存储对话历史到数据库
    - 获取对话历史
    - 多会话管理
    """
```

**主要方法：**
- `create_session()` - 创建新会话
- `save_message()` - 保存对话消息
- `get_history()` - 获取对话历史
- `get_user_sessions()` - 获取用户会话列表
- `delete_session()` - 删除会话

### 5. KnowledgeBase - 知识库

知识库核心模块，支持RAG：

```python
class KnowledgeBase:
    """
    特性：
    - 支持多种文件格式
    - 文本切片和向量化
    - 向量相似度搜索
    - 可选Rerank重排序
    """
```

**主要方法：**
- `add_text()` - 添加文本到知识库
- `add_document()` - 添加文档到知识库
- `search()` - 搜索知识库

## 数据流

### 对话流程

```
用户消息
    ↓
CustomerServiceAgent.chat()
    ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 会话管理                                             │
│    - 如果没有session_id，创建新会话                      │
│    - 获取对话历史（从数据库）                            │
├─────────────────────────────────────────────────────────┤
│ 2. 保存用户消息                                          │
│    - INSERT INTO conversations                           │
├─────────────────────────────────────────────────────────┤
│ 3. 知识库检索（如果启用）                                │
│    - KnowledgeBase.search()                              │
│    - 向量搜索 + Rerank                                   │
├─────────────────────────────────────────────────────────┤
│ 4. 构建增强Prompt                                        │
│    - 系统提示词 + 知识库上下文 + 对话历史 + 用户消息     │
├─────────────────────────────────────────────────────────┤
│ 5. 调用LLM生成回复                                       │
│    - agno Agent.arun()                                   │
├─────────────────────────────────────────────────────────┤
│ 6. 保存助手回复                                          │
│    - INSERT INTO conversations                           │
├─────────────────────────────────────────────────────────┤
│ 7. 返回响应                                              │
│    - ChatResult (success, reply, session_id, ...)        │
└─────────────────────────────────────────────────────────┘
```

## 数据库设计

### 核心表

| 表名 | 说明 |
|------|------|
| `ai_service.model_configs` | 模型配置 |
| `ai_service.prompts` | 提示词配置 |
| `ai_service.conversations` | 对话历史 |
| `ai_service.knowledge_documents` | 知识库文档 |
| `ai_service.system_logs` | 系统日志 |

### 表结构

#### conversations - 对话历史表

```sql
CREATE TABLE ai_service.conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    role VARCHAR(20) NOT NULL,  -- user/assistant
    content TEXT NOT NULL,
    agent_used VARCHAR(100),
    model_id VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### model_configs - 模型配置表

```sql
CREATE TABLE ai_service.model_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    base_url VARCHAR(255),
    api_key_encrypted TEXT,
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### prompts - 提示词表

```sql
CREATE TABLE ai_service.prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    system_prompt TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 扩展机制

### 添加新的Agent

1. 创建Agent类，继承基础Agent
2. 实现自定义逻辑
3. 注册到Agent管理器

### 添加新的知识库源

1. 实现知识库接口
2. 配置连接信息
3. 注册到知识库管理器

### 添加新的LLM提供商

1. 在model_configs表中添加配置
2. 设置base_url和api_key
3. 激活模型

## 性能优化

1. **连接池** - PostgreSQL和Redis连接池
2. **缓存** - 提示词和模型配置缓存
3. **异步** - FastAPI异步处理
4. **索引** - 数据库索引优化

## 安全考虑

1. **API密钥** - 存储在数据库，建议加密
2. **输入验证** - Pydantic模型验证
3. **SQL注入** - 参数化查询
4. **CORS** - 跨域配置
