# 贡献指南

感谢您对增强多模态LLM Agent项目的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 1. 报告问题
如果您发现了bug或有功能建议，请创建issue：
- 清晰描述问题
- 提供复现步骤
- 包含相关截图（如适用）
- 说明您的运行环境

### 2. 提交代码
1. Fork此仓库
2. 创建功能分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature-name`
5. 创建Pull Request

### 3. 代码规范

#### Python 后端规范
- 遵循PEP 8代码风格
- 使用TypeScript类型提示
- 添加适当的docstring
- 确保异步操作正确处理
- 使用依赖注入模式

#### React 前端规范
- 使用TypeScript进行类型安全
- 遵循React Hooks最佳实践
- 组件化设计和复用
- 使用Tailwind CSS进行样式设计
- 添加适当的错误处理

#### 通用规范
- 添加适当的注释
- 确保代码有测试覆盖
- 更新相关文档
- 遵循Git提交信息规范
- 进行代码审查

## 开发环境设置

### 后端开发
```bash
cd backend
pip install -r requirements.txt
# 启动Redis (可选)
redis-server --daemonize yes
# 启动后端服务
python -m uvicorn app.main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm start
```

## 项目结构

```
llm-agent/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── main.py         # 应用入口
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
├── frontend/               # React前端
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
├── docs/                 # 文档
└── tests/                # 测试文件
```

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm test
```

## 文档

- API文档：启动后端后访问 `/docs`
- 快速启动指南：查看 `STARTUP.md`
- 项目说明：查看 `README.md`
- 技术文档：查看 `docs/` 目录

## 开发指南

### 新增功能开发

#### 添加新的LLM模型
1. 在 `backend/app/services/llm_service.py` 中添加新模型支持
2. 在前端 `App.tsx` 中添加模型选项
3. 更新API文档

#### 添加新的记忆类型
1. 在 `backend/app/models/models.py` 中扩展Memory模型
2. 在 `backend/app/services/memory_service.py` 中添加处理逻辑
3. 更新前端types和API调用

#### 添加新的Agent类型
1. 在 `backend/app/services/agent_service.py` 中创建新的Agent类
2. 继承BaseAgent并实现execute_task方法
3. 在Agent API中注册新类型

#### 添加新的文档格式支持
1. 在 `backend/app/services/rag_service.py` 中扩展DocumentProcessor
2. 添加相应的解析器方法
3. 更新文件类型验证

### 性能优化

#### 向量搜索优化
- 使用FAISS的GPU加速（如果可用）
- 优化embedding模型选择
- 实现向量缓存机制

#### 内存管理优化
- 实现记忆清理策略
- 优化向量索引结构
- 添加内存使用监控

#### 数据库优化
- 添加数据库索引
- 实现查询优化
- 考虑读写分离

## 社区

- 提问：通过GitHub Issues
- 讨论：GitHub Discussions
- 邮件：[maintainer@example.com](mailto:maintainer@example.com)

## 版本管理

### 版本号规则
- 主版本号：不兼容的API更改
- 次版本号：向下兼容的功能新增
- 修订号：向下兼容的问题修复

### 发布流程
1. 更新版本号
2. 更新CHANGELOG.md
3. 创建发布标签
4. 构建和发布

## 许可证

通过贡献您的代码，您同意您的贡献将在MIT许可证下发布。

## 致谢

感谢所有为增强多模态LLM Agent项目做出贡献的开发者！