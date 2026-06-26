# 🚀 部署指南

本文档详细说明如何使用Docker部署 AI Agent Framework 系统。

## 📋 目录

- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [常见问题](#常见问题)

## 环境要求

| 软件 | 版本要求 |
|------|----------|
| Docker | 20+ |
| Docker Compose | 2+ |

## 快速部署

### 步骤1：克隆项目

```bash
git clone https://github.com/your-username/ai-agent-framework.git
cd ai-agent-framework
```

### 步骤2：配置环境

```bash
# 复制配置模板
cp config.docker.json config.json
```

编辑 `config.json`，配置数据库和Redis连接信息（Docker环境通常不需要修改）。

> **注意**：模型配置、提示词等业务配置在管理后台中管理，不需要在config.json中配置。

### 步骤3：启动服务

**Linux/Mac:**
```bash
chmod +x docker-start.sh
./docker-start.sh start
```

**Windows:**
```bash
docker-start.bat start
```

### 步骤4：访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ 管理后台 | http://localhost | React前端 |
| 🎮 聊天演示 | http://localhost/demo | 聊天界面 |
| 📚 API文档 | http://localhost/docs | Swagger UI |
| 🔧 后端API | http://localhost:7777 | 直接访问 |

## 配置说明

### PostgreSQL配置

```json
{
    "postgresql": {
        "default": {
            "host": "postgres",
            "port": 5432,
            "user": "ai_admin",
            "password": "ai_password_2024",
            "database": "ai_service"
        }
    }
}
```

### Redis配置

```json
{
    "redis": {
        "host": "redis",
        "port": 6379,
        "password": "ai_redis_2024",
        "db": 0
    }
}
```

### 业务配置

模型配置、提示词等业务配置在管理后台中管理：

1. 访问 http://localhost 打开管理后台
2. 在"模型配置"中添加LLM模型（填入API密钥）
3. 在"提示词管理"中编辑提示词
4. 在"知识库管理"中上传文档

### 端口映射

| 服务 | 容器端口 | 宿主机端口 |
|------|----------|------------|
| PostgreSQL | 5432 | 15432 |
| Redis | 6379 | 16379 |
| 后端API | 7777 | 7777 |
| 前端 | 80 | 80 |

## 常用命令

### 服务管理

```bash
# 启动服务
./docker-start.sh start

# 停止服务
./docker-start.sh stop

# 重启服务
./docker-start.sh restart

# 查看状态
./docker-start.sh status
```

### 日志查看

```bash
# 查看所有日志
./docker-start.sh logs

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f postgres
```

### 镜像管理

```bash
# 重新构建镜像
./docker-start.sh build

# 重新构建并启动
docker-compose up -d --build
```

### 数据管理

```bash
# 清理所有数据
./docker-start.sh clean

# 备份数据库
docker exec ai-postgres pg_dump -U ai_admin ai_service > backup.sql

# 恢复数据库
cat backup.sql | docker exec -i ai-postgres psql -U ai_admin ai_service
```

## 常见问题

### 1. 端口被占用

修改 `docker-compose.yml` 中的端口映射。

### 2. Docker启动失败

```bash
# 检查Docker是否运行
docker info

# 查看详细错误
docker-compose up
```

### 3. 数据库连接失败

```bash
# 检查数据库容器
docker-compose ps postgres

# 查看数据库日志
docker-compose logs postgres
```

### 4. 重新初始化数据库

```bash
docker-compose down
docker volume rm ai-agent-framework_postgres_data
docker-compose up -d
```
