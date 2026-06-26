# 🤖 AI Agent Framework

[English](./README.en.md) | 中文

> 基于agno框架的通用智能客服服务，支持知识库增强问答、多会话管理、对话持久化，可复用于任何行业

## ✨ 项目特点

- 🤖 **agno框架** - 基于agno的高性能Agent框架
- 📚 **知识库增强** - RAG管线，向量搜索+重排序
- 💾 **对话持久化** - 对话历史自动存储到数据库
- 🔀 **多会话管理** - 支持创建、切换、删除会话
- 📝 **提示词管理** - 数据库管理，实时生效
- ⚙️ **模型配置** - 多模型切换，无需重启
- 🔧 **通用框架** - 可配置、可扩展、可复用
- ⚡ **高性能** - FastAPI异步处理
- 🎨 **内置演示** - 开箱即用的聊天演示界面
- 🖥️ **管理后台** - React前端管理界面
- 🐳 **Docker部署** - 一键容器化启动

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (前端)                          │
├─────────────────────────────────────────────────────────┤
│                  /api/* → 后端代理                       │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Server                        │
├─────────────────────────────────────────────────────────┤
│              CustomerServiceAgent (agno)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  用户消息 → 知识库检索 → LLM生成 → 返回回复    │   │
│  │       ↓              ↓                          │   │
│  │  保存历史        会话管理                        │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL + pgvector  │  Redis  │  LangChain          │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent框架 | agno | 高性能AI Agent框架 |
| Web框架 | FastAPI | 异步Web框架 |
| 前端框架 | React + Vite | 管理后台 |
| RAG编排 | LangChain | 知识库检索增强 |
| 向量存储 | PostgreSQL + pgvector | 向量相似度搜索 |
| 缓存 | Redis | 提示词缓存 |
| 容器化 | Docker + Docker Compose | 一键部署 |

## 🚀 快速开始

### 环境要求

- Docker 20+
- Docker Compose 2+

### 启动步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-username/ai-agent-framework.git
cd ai-agent-framework

# 2. 配置环境
cp config.docker.json config.json
# 编辑config.json填入数据库和Redis连接信息

# 3. 启动服务
# Linux/Mac
chmod +x docker-start.sh
./docker-start.sh start

# Windows
docker-start.bat start
```

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🖥️ 管理后台 | http://localhost | React前端 |
| 🎮 聊天演示 | http://localhost/demo | 聊天界面 |
| 📚 API文档 | http://localhost/docs | Swagger UI |
| 🔧 后端API | http://localhost:7777 | 直接访问 |

### 常用命令

```bash
./docker-start.sh start    # 启动服务
./docker-start.sh stop     # 停止服务
./docker-start.sh restart  # 重启服务
./docker-start.sh logs     # 查看日志
./docker-start.sh status   # 查看状态
./docker-start.sh build    # 重新构建
./docker-start.sh clean    # 清理数据
```

## 📚 API接口

### 智能问答

**POST** `/api/agent/chat`

```json
{
  "message": "你好，请介绍一下自己",
  "user_id": "user_123",
  "session_id": "session_xxx",
  "use_knowledge_base": true
}
```

**响应:**
```json
{
  "success": true,
  "reply": "您好！我是AI智能客服助手...",
  "agent_used": "智能客服",
  "session_id": "session_abc123",
  "has_knowledge": false,
  "duration_ms": 1234
}
```

### 会话管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/agent/sessions` | GET | 获取用户会话列表 |
| `/api/agent/sessions/new` | POST | 创建新会话 |
| `/api/agent/sessions/{id}/history` | GET | 获取会话历史 |
| `/api/agent/sessions/{id}` | DELETE | 删除会话 |

### 系统管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/agent/info` | GET | 获取Agent信息 |
| `/api/agent/health` | GET | 健康检查 |
| `/api/agent/reset` | POST | 重置Agent |

### 管理后台API

| 模块 | 端点 | 说明 |
|------|------|------|
| 提示词 | `/api/admin/prompts` | 提示词管理 |
| 知识库 | `/api/admin/knowledge` | 知识库管理 |
| 模型 | `/api/admin/models` | 模型配置 |
| 对话 | `/api/admin/conversations` | 对话管理 |
| 监控 | `/api/admin/monitor` | 系统监控 |

## 🖥️ 管理后台功能

| 功能 | 说明 |
|------|------|
| 📊 仪表盘 | 系统概览、统计数据 |
| 💬 对话测试 | 在线聊天、实时测试 |
| 📝 提示词管理 | 创建、编辑、删除、测试提示词 |
| 📚 知识库管理 | 上传文档、向量化、搜索测试 |
| ⚙️ 模型配置 | 添加、切换、测试不同模型 |
| 📈 系统监控 | 日志、性能、健康检查 |

## 💻 使用示例

### Python

```python
import requests

# 创建会话
response = requests.post('http://localhost:7777/api/agent/sessions?user_id=user123')
session_id = response.json()['session_id']

# 发送消息
response = requests.post('http://localhost:7777/api/agent/chat', json={
    'message': '你好',
    'user_id': 'user123',
    'session_id': session_id
})
print(response.json()['reply'])

# 继续对话（自动加载历史）
response = requests.post('http://localhost:7777/api/agent/chat', json={
    'message': '我想查询订单',
    'user_id': 'user123',
    'session_id': session_id
})
print(response.json()['reply'])
```

### JavaScript

```javascript
// 创建会话
const sessionRes = await fetch('/api/agent/sessions/new?user_id=user123', { method: 'POST' });
const { session_id } = await sessionRes.json();

// 发送消息
const chatRes = await fetch('/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '你好',
    user_id: 'user123',
    session_id: session_id
  })
});
const data = await chatRes.json();
console.log(data.reply);
```

## 📁 项目结构

```
ai-agent-framework/
├── 📄 核心文件
│   ├── server.py                    # FastAPI主服务器
│   ├── config.docker.json          # 配置模板
│   └── requirements.txt             # Python依赖
│
├── 🐳 Docker配置
│   ├── Dockerfile                   # 后端镜像
│   ├── docker-compose.yml           # 容器编排
│   ├── docker-start.sh              # Linux启动脚本
│   └── docker-start.bat             # Windows启动脚本
│
├── 🤖 后端模块
│   ├── modules/
│   │   ├── agents/                  # 智能问答Agent
│   │   └── admin_api/               # 管理后台API
│   └── common/                      # 公共模块
│       ├── model_manager.py         # 模型管理
│       ├── prompt_manager.py        # 提示词管理
│       ├── conversation_manager.py  # 对话管理
│       └── knowledge_base.py        # 知识库
│
├── 🎨 前端管理后台
│   └── admin_frontend/
│       ├── Dockerfile               # 前端镜像
│       ├── nginx.conf               # Nginx配置
│       └── src/                     # React源码
│
├── 🗄️ 数据库
│   └── sql/init.sql                 # 初始化脚本
│
└── 📚 文档
    ├── README.md
    ├── ARCHITECTURE.md
    ├── DEPLOY.md
    └── CONTRIBUTING.md
```

## 🎯 适用场景

- 🛒 **电商客服** - 商品咨询、订单查询、售后服务
- 🏢 **企业客服** - 内部IT支持、HR咨询、行政服务
- 🏥 **医疗咨询** - 预约挂号、健康咨询、用药指导
- 📚 **教育辅导** - 课程咨询、学习辅导、考试答疑
- 💼 **金融服务** - 产品介绍、账户查询、投资建议

## 📖 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计
- [DEPLOY.md](./DEPLOY.md) - 部署指南
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 贡献指南

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE)

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

⭐ 如果这个项目对你有帮助，欢迎Star支持！
