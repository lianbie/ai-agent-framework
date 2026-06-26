"""
AI智能客服框架 - 主服务器

基于FastAPI + agno的通用智能客服服务。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
import os

# 配置日志
from common.log import setup_logger
logger = setup_logger(name="ai_service", log_file="logs/app.log")

# 创建FastAPI应用
app = FastAPI(
    title="AI智能客服框架",
    description="基于agno框架的通用智能客服服务，支持知识库增强问答",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 记录启动时间
_start_time = time.time()

# 导入路由
from modules.agents.routes import router as agent_router
from modules.admin_api.routes import router as admin_router
from modules.auth.routes import router as auth_router

# 注册路由
app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(admin_router)


# ============ 页面路由 ============

@app.get("/", response_class=HTMLResponse)
async def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI智能客服框架</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                text-align: center;
                color: white;
                padding: 40px;
            }
            h1 { font-size: 48px; margin-bottom: 20px; }
            p { font-size: 18px; opacity: 0.9; margin-bottom: 30px; }
            .buttons { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; }
            .btn {
                display: inline-block;
                padding: 15px 30px;
                background: white;
                color: #667eea;
                text-decoration: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 40px;
                max-width: 800px;
            }
            .feature {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 12px;
                backdrop-filter: blur(10px);
            }
            .feature h3 { margin-bottom: 10px; }
            .feature p { font-size: 14px; opacity: 0.8; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI智能客服框架</h1>
            <p>基于agno框架的通用智能客服服务</p>
            <div class="buttons">
                <a href="/demo" class="btn">🎮 在线演示</a>
                <a href="/docs" class="btn">📚 API文档</a>
                <a href="/redoc" class="btn">📖 API参考</a>
            </div>
            <div class="features">
                <div class="feature">
                    <h3>🤖 agno框架</h3>
                    <p>高性能AI Agent框架</p>
                </div>
                <div class="feature">
                    <h3>📚 知识库增强</h3>
                    <p>RAG管线，精准检索</p>
                </div>
                <div class="feature">
                    <h3>🔧 通用框架</h3>
                    <p>可复用于任何行业</p>
                </div>
                <div class="feature">
                    <h3>⚡ 高性能</h3>
                    <p>FastAPI异步处理</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """演示页面"""
    return FileResponse("templates/demo.html")


@app.get("/admin")
@app.get("/admin/{path:path}")
async def admin_page(path: str = ""):
    """管理后台页面"""
    # 检查是否存在构建后的前端文件
    admin_dist = "admin_frontend/dist"
    if os.path.exists(f"{admin_dist}/index.html"):
        return FileResponse(f"{admin_dist}/index.html")
    else:
        return HTMLResponse(
            """
            <html>
            <head><title>管理后台</title></head>
            <body>
                <h1>管理后台</h1>
                <p>前端项目尚未构建，请先执行：</p>
                <pre>
cd admin_frontend
npm install
npm run build
                </pre>
            </body>
            </html>
            """,
            status_code=200
        )


@app.get("/health")
async def health():
    """健康检查"""
    import psutil
    uptime = int(time.time() - _start_time)

    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": uptime,
        "memory_usage": psutil.Process().memory_info().rss / 1024 / 1024  # MB
    }


# ============ 启动事件 ============

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 60)
    logger.info("🚀 AI智能客服框架启动")
    logger.info("=" * 60)
    logger.info("📍 可用接口:")
    logger.info("  - POST /api/agent/chat         智能问答")
    logger.info("  - GET  /api/agent/health       健康检查")
    logger.info("  - GET  /api/agent/info         Agent信息")
    logger.info("  - GET  /api/admin/prompts      提示词管理")
    logger.info("  - GET  /api/admin/knowledge    知识库管理")
    logger.info("  - GET  /api/admin/models       模型配置")
    logger.info("  - GET  /api/admin/conversations 对话管理")
    logger.info("  - GET  /api/admin/monitor      系统监控")
    logger.info("  - GET  /demo                   演示页面")
    logger.info("  - GET  /admin                  管理后台")
    logger.info("  - GET  /docs                   API文档")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    from common.postgresql_pool import pg_pool
    from common.redis_client import redis_client

    pg_pool.close()
    redis_client.close()
    logger.info("👋 服务已关闭")
