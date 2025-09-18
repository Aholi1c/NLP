# 增强多模态LLM Agent - 快速启动指南 v2.0

## 环境准备

### 系统要求
- Python 3.8+
- Node.js 16+
- npm 或 yarn
- Redis (用于向量搜索和缓存)

### 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
cd frontend
npm install
```

## 配置

### 1. 环境变量配置

复制后端环境变量示例文件：
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，设置你的 OpenAI API 密钥：
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
DATABASE_URL=sqlite:///./llm_agent.db
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://localhost:6379/0
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./vector_store
```

### 2. 前端环境变量配置

在 `frontend` 目录下创建 `.env` 文件：
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 启动应用

### 启动后端服务
```bash
cd backend
# 启动Redis服务 (如果未运行)
redis-server --daemonize yes

# 启动FastAPI服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动前端服务
```bash
cd frontend
npm start
```

## 访问应用

- 前端界面: http://localhost:3000
- 后端API文档: http://localhost:8000/docs
- 后端健康检查: http://localhost:8000/health

## 功能特性

### 🎯 核心功能
- **文本对话**: 支持与AI进行实时文本对话
- **图像分析**: 上传图片进行分析和描述
- **语音交互**: 支持语音录制和转录
- **会话管理**: 创建、删除、管理对话历史
- **实时通信**: WebSocket支持流式响应

### 🚀 增强功能 (v2.0)
- **记忆系统**: 长期记忆、短期记忆和上下文管理
- **RAG增强**: 检索增强生成，基于知识库的智能问答
- **多Agent协作**: 多个AI助手协同工作
- **知识库管理**: 支持多种文档格式的知识库构建
- **向量搜索**: 基于embedding的语义搜索

### 🛠️ 技术特性
- **多模态支持**: 文本、图像、音频统一处理
- **流式响应**: 实时显示AI回复内容
- **会话持久化**: 对话历史自动保存
- **响应式界面**: 现代化Web界面设计
- **RESTful API**: 标准化的API接口
- **向量数据库**: 基于FAISS的高效向量搜索
- **多Agent架构**: 支持顺序、并行、层级协作模式

## 使用指南

### 基本对话
1. 在左侧边栏点击"+"创建新对话
2. 在输入框中输入消息
3. 点击发送或按Enter键发送消息
4. AI回复会实时显示在聊天区域

### 图像分析
1. 点击附件按钮📎上传图片
2. 在输入框中添加相关问题（可选）
3. 发送消息进行图像分析

### 语音交互
1. 点击麦克风按钮🎤开始录音
2. 说话完成后点击停止按钮⏹️
3. 系统会自动转录并发送消息

### 🚀 增强功能使用

#### 记忆系统
1. 点击"Show Advanced Features"按钮展开功能面板
2. 开启"🧠 记忆系统"开关
3. 系统会自动管理长期和短期记忆
4. AI会基于历史记忆提供更个性化的回答

#### RAG增强
1. 上传文档到知识库（支持PDF、DOCX、Markdown、HTML）
2. 在功能面板中开启"📚 RAG增强"
3. 选择要使用的知识库
4. AI会基于知识库内容回答问题

#### 多Agent协作
1. 在功能面板中开启"🤖 多Agent协作"
2. 选择参与协作的Agent类型
3. 选择协作方式（顺序执行、并行执行、层级协作）
4. 多个Agent会协同工作提供更全面的回答

### 会话管理
- **新建对话**: 点击左侧边栏的"+"按钮
- **切换对话**: 点击左侧边栏中的对话项
- **删除对话**: 鼠标悬停在对话项上点击删除按钮
- **搜索对话**: 使用顶部搜索框查找历史对话

## 开发指南

### 项目结构
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
└── docs/                # 项目文档
```

### API文档
启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

### 主要API端点
#### 基础聊天功能
- `POST /api/chat/chat` - 发送聊天消息
- `POST /api/chat/chat/upload` - 发送带文件的聊天消息
- `GET /api/chat/conversations` - 获取对话列表
- `POST /api/media/analyze-image/upload` - 分析上传的图像
- `POST /api/media/transcribe/upload` - 转录上传的音频

#### 增强功能API (v2.0)
- `POST /api/chat/enhanced` - 增强聊天（支持记忆、RAG、多Agent）
- `POST /api/chat/extract-memory` - 从对话提取记忆

#### 记忆系统API
- `POST /api/memory/memories` - 创建记忆
- `GET /api/memory/memories/search` - 搜索记忆
- `GET /api/memory/working-memory/{session_id}` - 获取工作记忆
- `PUT /api/memory/working-memory/{session_id}` - 更新工作记忆
- `POST /api/memory/memories/consolidate` - 整合记忆

#### RAG系统API
- `POST /api/rag/knowledge-bases` - 创建知识库
- `GET /api/rag/knowledge-bases` - 获取知识库列表
- `POST /api/rag/knowledge-bases/{kb_id}/upload` - 上传文档
- `POST /api/rag/knowledge-bases/search` - 搜索知识库
- `GET /api/rag/knowledge-bases/{kb_id}/stats` - 获取知识库统计

#### 多Agent系统API
- `GET /api/agents` - 获取活跃Agent列表
- `POST /api/agents/tasks` - 创建Agent任务
- `GET /api/agents/tasks/{session_id}` - 获取会话任务
- `POST /api/agents/collaborations` - 创建Agent协作
- `GET /api/agents/collaborations/{collab_id}` - 获取协作状态

### WebSocket事件
- `chat` - 发送聊天消息
- `chat_start` - 开始处理聊天消息
- `chat_chunk` - 流式响应内容块
- `chat_complete` - 聊天完成
- `transcribe` - 音频转录
- `analyze_image` - 图像分析

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本是否>=3.8
   - 确认已安装所有依赖: `pip install -r requirements.txt`
   - 检查8000端口是否被占用

2. **前端连接失败**
   - 确认后端服务已启动
   - 检查环境变量配置
   - 确认3000端口未被占用

3. **OpenAI API错误**
   - 检查API密钥是否正确
   - 确认API密钥有足够权限
   - 检查网络连接

4. **WebSocket连接问题**
   - 确认后端WebSocket服务正常运行
   - 检查防火墙设置
   - 验证WebSocket URL配置

### 日志查看
- 后端日志: 直接在终端查看
- 前端日志: 浏览器开发者工具控制台
- WebSocket日志: 浏览器Network面板

## 扩展功能

### 添加新的LLM模型
1. 在 `backend/app/services/llm_service.py` 中添加新模型支持
2. 在前端 `App.tsx` 中添加模型选项
3. 更新API文档

### 添加新的媒体类型
1. 在 `backend/app/services/media_service.py` 中添加处理逻辑
2. 更新数据模型和API接口
3. 在前端添加相应的UI组件

### 集成其他AI服务
1. 在 `services` 目录下创建新的服务类
2. 实现相应的API接口
3. 在前端添加调用逻辑

## 部署指南

### Docker部署
```bash
# 构建镜像
docker build -t llm-agent .

# 运行容器
docker run -p 8000:8000 -p 3000:3000 llm-agent
```

### 生产环境部署
1. 使用反向代理(Nginx)
2. 配置HTTPS证书
3. 设置环境变量
4. 使用进程管理器(supervisord)

## 许可证

MIT License