-- 认证系统数据库初始化脚本

-- 用户表
CREATE TABLE IF NOT EXISTS ai_service.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user',  -- admin, user
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 验证码表
CREATE TABLE IF NOT EXISTS ai_service.verify_codes (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    purpose VARCHAR(20) NOT NULL,  -- login, register, reset
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 登录日志表
CREATE TABLE IF NOT EXISTS ai_service.login_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ai_service.users(id),
    login_type VARCHAR(20) NOT NULL,  -- password, sms
    ip_address VARCHAR(50),
    user_agent TEXT,
    status VARCHAR(20) NOT NULL,  -- success, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_phone ON ai_service.users(phone);
CREATE INDEX IF NOT EXISTS idx_users_email ON ai_service.users(email);
CREATE INDEX IF NOT EXISTS idx_verify_codes_phone ON ai_service.verify_codes(phone);
CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON ai_service.login_logs(user_id);

-- 插入默认管理员账号
-- 密码: admin123 (SHA256 + salt)
INSERT INTO ai_service.users (username, email, phone, password_hash, nickname, role)
VALUES (
    'admin',
    'admin@example.com',
    '13800138000',
    'a1a9cbfd7dd79d66ca63c49fba231d01:64cb5335ae470c30d643d8927f3098fcaba0eaa412f4182e9914c89178217954',
    '管理员',
    'admin'
) ON CONFLICT (username) DO NOTHING;
