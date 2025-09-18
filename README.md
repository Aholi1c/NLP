# 增强多模态LLM Agent

一个功能齐全的增强多模态大语言模型代理应用，支持文本、图像、语音交互，并集成记忆系统、RAG增强和多Agent协作功能。

## 功能特性

### 🎯 核心功能
- 🎯 **多模态支持**: 文本、图像、语音输入输出
- 💬 **实时对话**: WebSocket支持实时通信
- 🗣️ **语音交互**: 语音识别和语音合成
- 🖼️ **图像理解**: 图像分析和描述生成
- 💾 **会话管理**: 历史记录和上下文保持
- 🌐 **响应式界面**: 现代化Web前端

### 🚀 增强功能 (v2.0)
- 🧠 **记忆系统**: 长期记忆、短期记忆和上下文管理
- 📚 **RAG增强**: 检索增强生成，基于知识库的智能问答
- 🤖 **多Agent协作**: 多个AI助手协同工作
- 🔍 **向量搜索**: 基于embedding的语义搜索
- 📄 **文档处理**: 支持PDF、DOCX、Markdown、HTML文件
- 🧩 **模块化架构**: 清晰的服务分离和扩展性

## 技术栈

### 后端
- **FastAPI**: 高性能Web框架
- **OpenAI API**: LLM推理服务
- **SQLite**: 主数据存储
- **FAISS**: 向量数据库
- **Redis**: 缓存和会话管理
- **Sentence Transformers**: 文本嵌入
- **Langchain**: RAG框架
- **WebSocket**: 实时通信
- **Pillow**: 图像处理
- **SpeechRecognition**: 语音识别
- **Unstructured**: 文档处理
- **Celery**: 异步任务处理

### 前端
- **React**: 现代JavaScript框架
- **TypeScript**: 类型安全
- **Tailwind CSS**: 样式框架
- **WebSocket**: 实时通信
- **HTML5**: 语音和图像API
- **Axios**: HTTP客户端

## 项目结构

```
llm-agent/
├── backend/                 # 后端FastAPI服务
│   ├── app/
│   │   ├── main.py         # 主应用入口
│   │   ├── models/         # 数据模型
│   │   │   ├── models.py   # 数据库模型
│   │   │   └── schemas.py  # Pydantic模式
│   │   ├── api/            # API路由
│   │   │   ├── chat.py     # 聊天相关API
│   │   │   ├── memory.py   # 记忆系统API
│   │   │   ├── rag.py      # RAG系统API
│   │   │   └── agents.py   # 多Agent系统API
│   │   ├── services/       # 业务逻辑
│   │   │   ├── llm_service.py      # LLM服务
│   │   │   ├── memory_service.py   # 记忆管理服务
│   │   │   ├── rag_service.py       # RAG服务
│   │   │   ├── agent_service.py    # 多Agent服务
│   │   │   ├── vector_service.py   # 向量搜索服务
│   │   │   └── media_service.py     # 媒体处理服务
│   │   └── core/           # 核心配置
│   ├── requirements.txt    # Python依赖
│   └── .env.example       # 环境变量示例
├── frontend/               # React前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── ChatInterface.tsx   # 聊天界面
│   │   │   ├── FeaturePanel.tsx     # 功能面板
│   │   │   └── ConversationList.tsx # 对话列表
│   │   ├── services/      # API和WebSocket服务
│   │   ├── types/         # TypeScript类型定义
│   │   └── App.tsx        # 主应用组件
│   ├── package.json       # Node.js依赖
│   └── public/           # 静态资源
├── vector_store/          # 向量数据库存储
└── docs/                # 文档
    ├── STARTUP.md       # 快速启动指南
    ├── CONTRIBUTING.md  # 贡献指南
    └── README.md        # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Redis (可选，用于缓存)

### 后端启动
```bash
cd backend
pip install -r requirements.txt
# 启动Redis (可选)
redis-server --daemonize yes
# 启动后端服务
python -m uvicorn app.main:app --reload
```

### 前端启动
```bash
cd frontend
npm install
npm start
```

## 配置

### 后端配置
复制 `backend/.env.example` 为 `backend/.env`：
```
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
DATABASE_URL=sqlite:///./llm_agent.db
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://localhost:6379/0
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./vector_store
```

### 前端配置
在 `frontend` 目录创建 `.env` 文件：
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 访问应用

- 前端界面: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- 后端健康检查: http://localhost:8000/health

## 增强功能使用

### 🧠 记忆系统
- 自动管理长期和短期记忆
- 基于重要性的记忆评分
- 上下文相关的记忆检索

### 📚 RAG增强
- 支持多种文档格式 (PDF, DOCX, Markdown, HTML)
- 智能文档分块和向量化
- 基于知识库的智能问答

### 🤖 多Agent协作
- 顺序、并行、层级协作模式
- 专业化Agent (研究员、分析师、作家、协调员)
- 任务分配和结果整合

## 许可证

MIT License