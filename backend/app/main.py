from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

from .core.config import settings
from .core.database import get_db, engine
from .models.models import Base
from .api import chat, media, memory, rag, agents
from .api.websocket import handle_websocket_chat, manager

# 加载环境变量
load_dotenv()

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="增强多模态LLM Agent API",
    description="具备记忆系统、RAG增强和多Agent协作的智能AI助手API",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# 包含API路由
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])

@app.get("/")
async def root():
    """
    根路径
    """
    return {
        "message": "多模态LLM Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "websocket": "/ws/{client_id}"
    }

@app.get("/health")
async def health_check():
    """
    健康检查
    """
    return {"status": "healthy", "service": "LLM Agent API"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket端点
    """
    await handle_websocket_chat(websocket, client_id)

@app.get("/api/connections")
async def get_connections():
    """
    获取当前连接数
    """
    return {
        "active_connections": len(manager.active_connections),
        "clients": list(manager.active_connections.keys())
    }

@app.on_event("startup")
async def startup_event():
    """
    启动事件
    """
    print("LLM Agent API starting up...")
    print(f"Upload directory: {settings.upload_dir}")
    print(f"Database URL: {settings.database_url}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    关闭事件
    """
    print("LLM Agent API shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )