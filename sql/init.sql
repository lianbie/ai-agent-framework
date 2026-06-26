-- AI智能客服框架 - 数据库初始化脚本

-- 创建schema
CREATE SCHEMA IF NOT EXISTS ai_service;

-- 设置search_path
SET search_path TO ai_service, public;

-- ============ 1. 提示词表 ============

CREATE TABLE IF NOT EXISTS ai_service.prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    system_prompt TEXT NOT NULL,
    variables JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_by VARCHAR(100) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_prompts_name ON ai_service.prompts(name);
CREATE INDEX IF NOT EXISTS idx_prompts_is_default ON ai_service.prompts(is_default);

-- 插入默认提示词
INSERT INTO ai_service.prompts (name, description, system_prompt, is_default, version)
VALUES (
    'default',
    '默认智能客服提示词',
    '你是一个专业的智能客服助手。

你的职责是：
1. 礼貌、专业地回答用户问题
2. 基于知识库内容提供准确信息
3. 如果不确定答案，诚实告知用户
4. 保持友好、耐心的服务态度

回答要求：
- 简洁明了，重点突出
- 使用用户能理解的语言
- 必要时提供分步骤说明',
    TRUE,
    1
) ON CONFLICT (name) DO NOTHING;


-- ============ 2. 知识库文档表 ============

CREATE TABLE IF NOT EXISTS ai_service.knowledge_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_knowledge_docs_status ON ai_service.knowledge_documents(status);
CREATE INDEX IF NOT EXISTS idx_knowledge_docs_created ON ai_service.knowledge_documents(created_at);


-- ============ 3. 模型配置表 ============

CREATE TABLE IF NOT EXISTS ai_service.model_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- openai, anthropic, ollama, etc.
    model_id VARCHAR(100) NOT NULL,
    base_url VARCHAR(255),
    api_key_encrypted TEXT,
    parameters JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_model_configs_provider ON ai_service.model_configs(provider);
CREATE INDEX IF NOT EXISTS idx_model_configs_is_active ON ai_service.model_configs(is_active);

-- 插入默认模型配置
INSERT INTO ai_service.model_configs (name, provider, model_id, base_url, parameters, is_active)
VALUES (
    'GPT-4o Mini',
    'openai',
    'gpt-4o-mini',
    'https://api.openai.com/v1',
    '{"temperature": 0.7, "max_tokens": 2000}',
    TRUE
) ON CONFLICT DO NOTHING;


-- ============ 4. 对话历史表 ============

CREATE TABLE IF NOT EXISTS ai_service.conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    role VARCHAR(20) NOT NULL,  -- user, assistant, system
    content TEXT NOT NULL,
    agent_used VARCHAR(100),
    prompt_id INTEGER REFERENCES ai_service.prompts(id),
    model_id VARCHAR(100),
    tokens_used INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_conversations_session ON ai_service.conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON ai_service.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON ai_service.conversations(created_at);


-- ============ 5. 系统日志表 ============

CREATE TABLE IF NOT EXISTS ai_service.system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,  -- DEBUG, INFO, WARNING, ERROR
    module VARCHAR(100),
    message TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON ai_service.system_logs(level);
CREATE INDEX IF NOT EXISTS idx_system_logs_created ON ai_service.system_logs(created_at);


-- ============ 6. API调用统计表 ============

CREATE TABLE IF NOT EXISTS ai_service.api_stats (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER,
    duration_ms INTEGER,
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_api_stats_endpoint ON ai_service.api_stats(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_stats_created ON ai_service.api_stats(created_at);


-- ============ 创建更新时间触发器 ============

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON ai_service.prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_documents_updated_at
    BEFORE UPDATE ON ai_service.knowledge_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_model_configs_updated_at
    BEFORE UPDATE ON ai_service.model_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============ 授权 ============

-- 如果存在ai_admin用户，授予所有权限
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'ai_admin') THEN
        GRANT ALL PRIVILEGES ON SCHEMA ai_service TO ai_admin;
        GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ai_service TO ai_admin;
        GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ai_service TO ai_admin;
    END IF;
END $$;
