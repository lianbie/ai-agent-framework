# 🤖 AI Agent Framework

<p align="center">
  <strong>基于 agno 构建的企业级 AI 智能客服系统</strong>
</p>

<p align="center">
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.9+-green.svg" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Docker-Supported-brightgreen.svg" alt="Docker"></a>
</p>

<p align="center">
  <a href="#-快速开始">快速开始</a> •
  <a href="#-核心特性">核心特性</a> •
  <a href="#-api接口">API接口</a> •
  <a href="#-文档">文档</a>
</p>

## 📖 简介

AI Agent Framework 是一个**开箱即用**的 AI 智能客服系统。支持知识库增强问答、流式对话、多模型切换、会话管理，**Docker 一键部署**，3 分钟即可运行。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 智能问答 | 流式响应 + 多轮对话，体验丝滑 |
| 📚 知识库 RAG | 文档上传 → 向量化 → 智能检索 |
| ⚙️ 多模型切换 | OpenAI / DeepSeek / 豆包，管理后台一键切换 |
| 📝 提示词管理 | 可视化编辑，实时生效，无需重启 |
| 💾 会话持久化 | 对话历史自动存储，支持多会话 |
| 🔐 登录认证 | 验证码登录 + JWT Token |
| 🖥️ 管理后台 | React 前端，仪表盘 + 对话测试 + 系统监控 |
| 🐳 一键部署 | `docker-compose up -d` 完事 |

## 🚀 快速开始

```bash
# 1. 克隆
git clone https://github.com/lianbie/ai-agent-framework.git
cd ai-agent-framework

# 2. 配置（可选，Docker自带默认配置）
cp config.docker.json config.json

# 3. 启动
docker-compose up -d
```

**访问：**
| 地址 | 说明 |
|------|------|
| `http://localhost` | 管理后台（默认账号 admin/admin123） |
| `http://localhost/demo` | 聊天演示 |
| `http://localhost/docs` | API 文档 |

## 🏗️ 架构

```
用户请求 → Nginx → FastAPI → Agent(agno) → LLM
                      ↓
         知识库检索 ← PostgreSQL+pgvector
                      ↓
         会话存储 ← PostgreSQL + Redis
```

## 🛠️ 技术栈

`agno` `FastAPI` `React` `LangChain` `PostgreSQL+pgvector` `Redis` `Docker`

## 📚 API接口

```python
import requests

# 发送消息
response = requests.post('http://localhost:7777/api/agent/chat', json={
    'message': '你好',
    'user_id': 'user_123'
})
print(response.json()['reply'])
```

**核心 API：**
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/agent/chat` | POST | 智能问答 |
| `/api/agent/chat/stream` | POST | 流式问答（SSE） |
| `/api/agent/sessions` | GET | 会话列表 |
| `/api/auth/login/password` | POST | 密码登录 |
| `/api/admin/prompts` | GET/POST | 提示词管理 |
| `/api/admin/knowledge/upload` | POST | 上传知识库文档 |
| `/api/admin/models` | GET/POST | 模型配置 |

## 🖥️ 管理后台

登录 `http://localhost`，即可使用：

- 📊 **仪表盘** — 系统概览、统计数据
- 💬 **对话测试** — 在线聊天，流式响应
- 📝 **提示词管理** — 增删改查，实时生效
- 📚 **知识库管理** — 上传文档，向量化检索
- ⚙️ **模型配置** — 添加/切换 LLM 模型
- 📈 **系统监控** — 日志、性能、健康检查

## 📁 目录结构

```
ai-agent-framework/
├── server.py                 # 入口
├── docker-compose.yml        # 一键部署
├── modules/
│   ├── agents/               # 智能问答 Agent
│   ├── admin_api/            # 管理后台 API
│   └── auth/                 # 认证模块
├── admin_frontend/           # React 前端
├── common/                   # 公共模块（DB/Redis/知识库）
├── sql/                      # 建表脚本
└── docs/                     # 文档
```

## 🎯 适用场景

`电商客服` `企业IT支持` `医疗咨询` `教育辅导` `金融服务` ··· 任何需要智能客服的场景

## 📖 文档

- [架构设计](./ARCHITECTURE.md) — 详细架构和数据流
- [部署指南](./DEPLOY.md) — 生产环境部署
- [贡献指南](./CONTRIBUTING.md)

## 📄 License

MIT © [lianbie](https://github.com/lianbie)

---

⭐ **如果对你有帮助，欢迎 Star！**
