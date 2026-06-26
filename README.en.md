# 🤖 AI Agent Framework

English | [中文](./README.md)

> A generic AI customer service framework based on agno, supporting knowledge base enhanced Q&A, multi-session management, and conversation persistence

## ✨ Features

- 🤖 **agno Framework** - High-performance AI Agent framework
- 📚 **Knowledge Base Enhancement** - RAG pipeline with vector search + reranking
- 💾 **Conversation Persistence** - Auto-save conversation history to database
- 🔀 **Multi-session Management** - Create, switch, delete sessions
- 📝 **Prompt Management** - Database management, real-time effect
- ⚙️ **Model Configuration** - Switch models without restart
- 🔧 **Generic Framework** - Configurable, extensible, reusable
- ⚡ **High Performance** - FastAPI async processing
- 🎨 **Built-in Demo** - Ready-to-use chat demo interface
- 🖥️ **Admin Panel** - React frontend management interface
- 🐳 **Docker Deployment** - One-click containerized startup

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Frontend)                      │
├─────────────────────────────────────────────────────────┤
│                  /api/* → Backend Proxy                  │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Server                        │
├─────────────────────────────────────────────────────────┤
│              CustomerServiceAgent (agno)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  User Query → Knowledge Retrieval → LLM → Reply │   │
│  │       ↓              ↓                          │   │
│  │  Save History    Session Management             │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  PostgreSQL + pgvector  │  Redis  │  LangChain          │
└─────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology | Description |
|-----------|------------|-------------|
| Agent Framework | agno | High-performance AI Agent framework |
| Web Framework | FastAPI | Async web framework |
| Frontend | React + Vite | Admin panel |
| RAG Orchestration | LangChain | Knowledge base retrieval enhancement |
| Vector Store | PostgreSQL + pgvector | Vector similarity search |
| Cache | Redis | Prompt caching |
| Containerization | Docker + Docker Compose | One-click deployment |

## 🚀 Quick Start

### Prerequisites

- Docker 20+
- Docker Compose 2+

### Installation

```bash
# 1. Clone the project
git clone https://github.com/your-username/ai-agent-framework.git
cd ai-agent-framework

# 2. Configure environment
cp config.docker.json config.json
# Edit config.json with database and Redis connection info

# 3. Start services
# Linux/Mac
chmod +x docker-start.sh
./docker-start.sh start

# Windows
docker-start.bat start
```

### Access URLs

| Service | URL | Description |
|---------|-----|-------------|
| 🖥️ Admin Panel | http://localhost | React frontend |
| 🎮 Chat Demo | http://localhost/demo | Chat interface |
| 📚 API Docs | http://localhost/docs | Swagger UI |
| 🔧 Backend API | http://localhost:7777 | Direct access |

### Common Commands

```bash
./docker-start.sh start    # Start services
./docker-start.sh stop     # Stop services
./docker-start.sh restart  # Restart services
./docker-start.sh logs     # View logs
./docker-start.sh status   # Check status
./docker-start.sh build    # Rebuild images
./docker-start.sh clean    # Clean all data
```

## 📚 API Endpoints

### Chat

**POST** `/api/agent/chat`

```json
{
  "message": "Hello, introduce yourself",
  "user_id": "user_123",
  "session_id": "session_xxx",
  "use_knowledge_base": true
}
```

**Response:**
```json
{
  "success": true,
  "reply": "Hello! I'm an AI customer service assistant...",
  "agent_used": "Customer Service",
  "session_id": "session_abc123",
  "has_knowledge": false,
  "duration_ms": 1234
}
```

### Session Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent/sessions` | GET | Get user sessions |
| `/api/agent/sessions/new` | POST | Create new session |
| `/api/agent/sessions/{id}/history` | GET | Get session history |
| `/api/agent/sessions/{id}` | DELETE | Delete session |

### System Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent/info` | GET | Get agent info |
| `/api/agent/health` | GET | Health check |
| `/api/agent/reset` | POST | Reset agent |

### Admin API

| Module | Endpoint | Description |
|--------|----------|-------------|
| Prompts | `/api/admin/prompts` | Prompt management |
| Knowledge | `/api/admin/knowledge` | Knowledge base management |
| Models | `/api/admin/models` | Model configuration |
| Conversations | `/api/admin/conversations` | Conversation management |
| Monitor | `/api/admin/monitor` | System monitoring |

## 🖥️ Admin Panel Features

| Feature | Description |
|---------|-------------|
| 📊 Dashboard | System overview, statistics |
| 💬 Chat Test | Online chat, real-time testing |
| 📝 Prompt Management | Create, edit, delete, test prompts |
| 📚 Knowledge Base | Upload documents, vectorize, search test |
| ⚙️ Model Config | Add, switch, test different models |
| 📈 System Monitor | Logs, performance, health check |

## 💻 Usage Examples

### Python

```python
import requests

# Create session
response = requests.post('http://localhost:7777/api/agent/sessions?user_id=user123')
session_id = response.json()['session_id']

# Send message
response = requests.post('http://localhost:7777/api/agent/chat', json={
    'message': 'Hello',
    'user_id': 'user123',
    'session_id': session_id
})
print(response.json()['reply'])

# Continue conversation (auto-loads history)
response = requests.post('http://localhost:7777/api/agent/chat', json={
    'message': 'I want to check my order',
    'user_id': 'user123',
    'session_id': session_id
})
print(response.json()['reply'])
```

### JavaScript

```javascript
// Create session
const sessionRes = await fetch('/api/agent/sessions/new?user_id=user123', { method: 'POST' });
const { session_id } = await sessionRes.json();

// Send message
const chatRes = await fetch('/api/agent/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello',
    user_id: 'user123',
    session_id: session_id
  })
});
const data = await chatRes.json();
console.log(data.reply);
```

## 📁 Project Structure

```
ai-agent-framework/
├── 📄 Core Files
│   ├── server.py                    # FastAPI main server
│   ├── config.docker.json          # Config template
│   └── requirements.txt             # Python dependencies
│
├── 🐳 Docker Config
│   ├── Dockerfile                   # Backend image
│   ├── docker-compose.yml           # Container orchestration
│   ├── docker-start.sh              # Linux startup script
│   └── docker-start.bat             # Windows startup script
│
├── 🤖 Backend Modules
│   ├── modules/
│   │   ├── agents/                  # Q&A Agent
│   │   └── admin_api/               # Admin API
│   └── common/                      # Common modules
│       ├── model_manager.py         # Model management
│       ├── prompt_manager.py        # Prompt management
│       ├── conversation_manager.py  # Conversation management
│       └── knowledge_base.py        # Knowledge base
│
├── 🎨 Frontend Admin
│   └── admin_frontend/
│       ├── Dockerfile               # Frontend image
│       ├── nginx.conf               # Nginx config
│       └── src/                     # React source
│
├── 🗄️ Database
│   └── sql/init.sql                 # Init script
│
└── 📚 Documentation
    ├── README.md
    ├── ARCHITECTURE.md
    ├── DEPLOY.md
    └── CONTRIBUTING.md
```

## 🎯 Use Cases

- 🛒 **E-commerce** - Product consultation, order tracking, after-sales
- 🏢 **Enterprise** - IT support, HR consultation, admin services
- 🏥 **Healthcare** - Appointment booking, health advice, medication guidance
- 📚 **Education** - Course consultation, tutoring, exam preparation
- 💼 **Finance** - Product introduction, account inquiry, investment advice

## 📖 Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture design
- [DEPLOY.md](./DEPLOY.md) - Deployment guide
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contributing guide

## 📄 License

MIT License - See [LICENSE](./LICENSE)

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

⭐ If this project helps you, please give it a Star!
