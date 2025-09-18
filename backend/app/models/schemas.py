from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class UserRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class UserCreate(BaseModel):
    username: str
    email: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class MessageCreate(BaseModel):
    conversation_id: int
    role: UserRole
    content: str
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: UserRole
    content: str
    message_type: MessageType
    media_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    user_id: Optional[int] = None

class ConversationResponse(BaseModel):
    id: int
    user_id: Optional[int]
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    model_used: str
    tokens_used: Optional[int] = None

class SpeechRequest(BaseModel):
    text: str
    language: str = "en"
    voice: Optional[str] = None

class SpeechResponse(BaseModel):
    audio_url: str
    duration: Optional[float] = None

class TranscriptionRequest(BaseModel):
    audio_url: str
    language: Optional[str] = None

class TranscriptionResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None

class ImageAnalysisRequest(BaseModel):
    image_url: str
    prompt: Optional[str] = "Describe this image in detail."

class ImageAnalysisResponse(BaseModel):
    analysis: str
    description: str
    tags: Optional[List[str]] = None

class AgentConfig(BaseModel):
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: Optional[str] = None

class AgentSessionCreate(BaseModel):
    config: AgentConfig
    user_id: Optional[int] = None

class AgentSessionResponse(BaseModel):
    session_id: str
    config: AgentConfig
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size: int
    file_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 记忆系统schemas
class MemoryType(str, Enum):
    EPISODIC = "episodic"  # 情景记忆
    SEMANTIC = "semantic"  # 语义记忆
    WORKING = "working"    # 工作记忆

class MemoryCreate(BaseModel):
    content: str
    memory_type: MemoryType = MemoryType.EPISODIC
    importance_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    user_id: Optional[int] = None

class MemoryResponse(BaseModel):
    id: int
    content: str
    memory_type: MemoryType
    importance_score: float
    access_count: int
    last_accessed: datetime
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True

class MemorySearchRequest(BaseModel):
    query: str
    memory_type: Optional[MemoryType] = None
    limit: int = 10
    threshold: float = 0.7
    user_id: Optional[int] = None

class WorkingMemoryUpdate(BaseModel):
    session_id: str
    context_data: Optional[Dict[str, Any]] = None
    short_term_memory: Optional[Dict[str, Any]] = None
    expires_in: Optional[int] = None  # 过期时间（秒）

# RAG系统schemas
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    user_id: Optional[int] = None

class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_id: Optional[int]
    document_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentUploadRequest(BaseModel):
    knowledge_base_id: int
    file_path: str
    chunk_size: int = 1000
    chunk_overlap: int = 200

class DocumentResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    original_name: str
    file_type: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RAGSearchRequest(BaseModel):
    query: str
    knowledge_base_ids: List[int] = []
    limit: int = 5
    threshold: float = 0.7
    filters: Optional[Dict[str, Any]] = None

class RAGSearchResult(BaseModel):
    content: str
    document_id: int
    chunk_index: int
    score: float
    metadata: Optional[Dict[str, Any]] = None

# 多Agent系统schemas
class AgentType(str, Enum):
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"

class AgentCreate(BaseModel):
    name: str
    description: str
    agent_type: AgentType
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    agent_type: AgentType
    capabilities: List[str]
    config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskCreate(BaseModel):
    agent_id: int
    session_id: str
    task_type: str
    task_data: Dict[str, Any]
    priority: int = 0

class TaskResponse(BaseModel):
    id: int
    task_id: str
    agent_id: int
    session_id: str
    task_type: str
    status: TaskStatus
    task_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CollaborationType(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"

class AgentCollaborationCreate(BaseModel):
    session_id: str
    collaboration_type: CollaborationType
    participants: List[int]  # Agent IDs
    workflow: Dict[str, Any]
    task_data: Dict[str, Any]

class AgentCollaborationResponse(BaseModel):
    id: int
    session_id: str
    collaboration_type: CollaborationType
    participants: List[Dict[str, Any]]
    workflow: Dict[str, Any]
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

# 增强的聊天请求
class EnhancedChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    message_type: MessageType = MessageType.TEXT
    media_url: Optional[str] = None
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    # 新增功能
    use_memory: bool = True
    use_rag: bool = True
    knowledge_base_ids: Optional[List[int]] = None
    agent_collaboration: bool = False
    collaboration_type: Optional[CollaborationType] = None
    agents: Optional[List[int]] = None

class EnhancedChatResponse(BaseModel):
    response: str
    conversation_id: int
    message_id: int
    model_used: str
    tokens_used: Optional[int] = None
    # 新增信息
    memory_used: bool = False
    rag_results: Optional[List[RAGSearchResult]] = None
    agent_collaboration: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None