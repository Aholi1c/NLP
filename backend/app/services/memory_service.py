from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from ..models.models import Memory, WorkingMemory, User
from ..models.schemas import MemoryCreate, MemoryResponse, WorkingMemoryUpdate, MemorySearchRequest
from ..services.vector_service import vector_service
from ..services.llm_service import llm_service
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from collections import Counter
import asyncio

# 下载NLTK数据（第一次运行时）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class MemoryService:
    def __init__(self, db: Session):
        self.db = db
        self.stop_words = set(stopwords.words('english'))

    async def create_memory(self, memory_data: MemoryCreate) -> MemoryResponse:
        """创建新的记忆"""
        try:
            # 提取关键词和重要性分数
            keywords, importance_score = self._extract_keywords_and_importance(memory_data.content)

            # 创建记忆记录
            memory = Memory(
                content=memory_data.content,
                memory_type=memory_data.memory_type,
                importance_score=importance_score,
                user_id=memory_data.user_id,
                metadata=memory_data.metadata or {},
                tags=memory_data.tags or keywords
            )

            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)

            # 添加到向量索引
            await asyncio.to_thread(
                vector_service.add_memory_embedding,
                memory.id, memory.content, self.db
            )

            return MemoryResponse.from_orm(memory)

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create memory: {e}")

    def search_memories(self, search_request: MemorySearchRequest) -> List[MemoryResponse]:
        """搜索记忆"""
        try:
            # 使用向量搜索
            similar_memories = vector_service.search_similar_memories(
                query=search_request.query,
                limit=search_request.limit,
                threshold=search_request.threshold,
                user_id=search_request.user_id,
                memory_type=search_request.memory_type,
                db=self.db
            )

            # 转换为MemoryResponse
            results = []
            for mem_data in similar_memories:
                memory_response = MemoryResponse(
                    id=mem_data["id"],
                    content=mem_data["content"],
                    memory_type=mem_data["memory_type"],
                    importance_score=mem_data["importance_score"],
                    access_count=mem_data.get("access_count", 0),
                    last_accessed=datetime.fromisoformat(mem_data["created_at"]),
                    created_at=datetime.fromisoformat(mem_data["created_at"]),
                    metadata=mem_data.get("metadata", {}),
                    tags=mem_data.get("tags", [])
                )
                results.append(memory_response)

            return results

        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def get_working_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取工作记忆"""
        try:
            working_memory = self.db.query(WorkingMemory).filter(
                WorkingMemory.session_id == session_id,
                WorkingMemory.is_active == True
            ).first()

            if working_memory:
                # 检查是否过期
                if working_memory.expires_at and working_memory.expires_at < datetime.utcnow():
                    working_memory.is_active = False
                    self.db.commit()
                    return None

                return {
                    "context_data": working_memory.context_data or {},
                    "short_term_memory": working_memory.short_term_memory or {},
                    "expires_at": working_memory.expires_at
                }

            return None

        except Exception as e:
            print(f"Error getting working memory: {e}")
            return None

    def update_working_memory(self, update_data: WorkingMemoryUpdate) -> Dict[str, Any]:
        """更新工作记忆"""
        try:
            working_memory = self.db.query(WorkingMemory).filter(
                WorkingMemory.session_id == update_data.session_id
            ).first()

            if not working_memory:
                # 创建新的工作记忆
                expires_at = None
                if update_data.expires_in:
                    expires_at = datetime.utcnow() + timedelta(seconds=update_data.expires_in)

                working_memory = WorkingMemory(
                    session_id=update_data.session_id,
                    context_data=update_data.context_data or {},
                    short_term_memory=update_data.short_term_memory or {},
                    expires_at=expires_at
                )
                self.db.add(working_memory)
            else:
                # 更新现有工作记忆
                if update_data.context_data is not None:
                    current_context = working_memory.context_data or {}
                    current_context.update(update_data.context_data)
                    working_memory.context_data = current_context

                if update_data.short_term_memory is not None:
                    current_memory = working_memory.short_term_memory or {}
                    current_memory.update(update_data.short_term_memory)
                    working_memory.short_term_memory = current_memory

                if update_data.expires_in:
                    working_memory.expires_at = datetime.utcnow() + timedelta(seconds=update_data.expires_in)

                working_memory.is_active = True

            self.db.commit()
            self.db.refresh(working_memory)

            return {
                "context_data": working_memory.context_data or {},
                "short_term_memory": working_memory.short_term_memory or {},
                "expires_at": working_memory.expires_at
            }

        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to update working memory: {e}")

    def clear_working_memory(self, session_id: str):
        """清除工作记忆"""
        try:
            working_memory = self.db.query(WorkingMemory).filter(
                WorkingMemory.session_id == session_id
            ).first()

            if working_memory:
                working_memory.is_active = False
                self.db.commit()

        except Exception as e:
            print(f"Error clearing working memory: {e}")

    async def consolidate_memories(self, user_id: Optional[int] = None):
        """整合记忆，将工作记忆转移到长期记忆"""
        try:
            # 获取所有活跃的工作记忆
            working_memories = self.db.query(WorkingMemory).filter(
                WorkingMemory.is_active == True
            ).all()

            for wm in working_memories:
                if user_id and wm.context_data and wm.context_data.get("user_id") != user_id:
                    continue

                # 将重要的工作记忆转为长期记忆
                if wm.short_term_memory:
                    for key, value in wm.short_term_memory.items():
                        if self._is_important_memory(key, value):
                            memory_content = f"Context: {wm.context_data}\nKey Information: {key} - {value}"

                            memory_data = MemoryCreate(
                                content=memory_content,
                                memory_type="episodic",
                                importance_score=0.7,
                                metadata={"source": "working_memory", "session_id": wm.session_id}
                            )

                            await self.create_memory(memory_data)

                # 清除工作记忆
                wm.is_active = False

            self.db.commit()

        except Exception as e:
            print(f"Error consolidating memories: {e}")

    async def extract_and_store_conversation_memory(self, conversation_id: int, user_id: Optional[int] = None):
        """从对话中提取并存储重要信息到记忆"""
        try:
            from ..models.models import Message

            # 获取对话的所有消息
            messages = self.db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at.asc()).all()

            if not messages:
                return

            # 使用LLM提取重要信息
            conversation_text = "\n".join([
                f"{msg.role}: {msg.content}" for msg in messages
            ])

            extraction_prompt = f"""
            Analyze the following conversation and extract important information that should be remembered.
            Focus on:
            - User preferences and interests
            - Important facts mentioned
            - Decisions made
            - Action items
            - Personal information shared

            Conversation:
            {conversation_text}

            Return a JSON object with extracted memories in the format:
            {{
                "memories": [
                    {{
                        "content": "specific fact or information",
                        "importance": 0.8,
                        "tags": ["preference", "fact"],
                        "type": "semantic"
                    }}
                ]
            }}
            """

            response = await llm_service.chat_completion([
                {"role": "system", "content": "You are a memory extraction expert. Extract important information from conversations."},
                {"role": "user", "content": extraction_prompt}
            ])

            try:
                # 解析LLM响应
                import json
                result = json.loads(response["content"])

                for mem_data in result.get("memories", []):
                    memory_create = MemoryCreate(
                        content=mem_data["content"],
                        memory_type=mem_data.get("type", "semantic"),
                        importance_score=mem_data.get("importance", 0.5),
                        tags=mem_data.get("tags", []),
                        user_id=user_id,
                        metadata={"source": "conversation", "conversation_id": conversation_id}
                    )

                    await self.create_memory(memory_create)

            except json.JSONDecodeError:
                print("Failed to parse memory extraction response")

        except Exception as e:
            print(f"Error extracting conversation memory: {e}")

    def _extract_keywords_and_importance(self, text: str) -> Tuple[List[str], float]:
        """提取关键词和重要性分数"""
        try:
            # 简单的关键词提取
            words = re.findall(r'\b\w+\b', text.lower())
            words = [w for w in words if w not in self.stop_words and len(w) > 2]

            word_freq = Counter(words)
            keywords = [word for word, freq in word_freq.most_common(5)]

            # 计算重要性分数（基于长度、关键词密度等）
            importance_score = min(1.0, len(keywords) / 10.0)
            if any(keyword in text.lower() for keyword in ["important", "remember", "note", "key"]):
                importance_score += 0.2
            if "?" in text or "!" in text:
                importance_score += 0.1

            return keywords, min(1.0, importance_score)

        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return [], 0.5

    def _is_important_memory(self, key: str, value: Any) -> bool:
        """判断是否为重要记忆"""
        important_keywords = [
            "preference", "important", "remember", "key", "decision",
            "goal", "objective", "plan", "strategy", "personal"
        ]

        text = f"{key} {str(value)}".lower()
        return any(keyword in text for keyword in important_keywords)

    async def get_relevant_context(self, query: str, session_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取相关的上下文信息"""
        try:
            # 搜索相关记忆
            relevant_memories = self.search_memories(MemorySearchRequest(
                query=query,
                limit=5,
                threshold=0.6,
                user_id=user_id
            ))

            # 获取工作记忆
            working_memory = self.get_working_memory(session_id)

            # 构建上下文
            context = {
                "relevant_memories": [
                    {
                        "content": mem.content,
                        "type": mem.memory_type,
                        "importance": mem.importance_score
                    } for mem in relevant_memories
                ],
                "working_memory": working_memory or {},
                "session_context": {
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

            return context

        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return {}

    async def update_memory_access(self, memory_id: int):
        """更新记忆访问记录"""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.access_count += 1
                memory.last_accessed = datetime.utcnow()
                self.db.commit()

        except Exception as e:
            print(f"Error updating memory access: {e}")

# 全局记忆服务实例（需要通过依赖注入使用）
def get_memory_service(db: Session) -> MemoryService:
    return MemoryService(db)