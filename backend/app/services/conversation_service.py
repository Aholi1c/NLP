from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.models import Conversation, Message, User
from ..models.schemas import ConversationCreate, MessageCreate, ChatRequest, ChatResponse
from ..services.llm_service import llm_service
from datetime import datetime
import uuid

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_conversation(self, conversation_data: ConversationCreate, user_id: Optional[int] = None) -> Conversation:
        """
        创建新对话
        """
        conversation = Conversation(
            title=conversation_data.title,
            user_id=user_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int) -> Optional[Conversation]:
        """
        获取对话详情
        """
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_user_conversations(self, user_id: Optional[int] = None, limit: int = 50) -> List[Conversation]:
        """
        获取用户的对话列表
        """
        query = self.db.query(Conversation)
        if user_id:
            query = query.filter(Conversation.user_id == user_id)
        return query.order_by(Conversation.updated_at.desc()).limit(limit).all()

    def add_message(self, message_data: MessageCreate) -> Message:
        """
        添加消息到对话
        """
        message = Message(
            conversation_id=message_data.conversation_id,
            role=message_data.role,
            content=message_data.content,
            message_type=message_data.message_type,
            media_url=message_data.media_url
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        # 更新对话的更新时间
        conversation = self.get_conversation(message_data.conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            self.db.commit()

        return message

    def get_conversation_messages(self, conversation_id: int) -> List[Message]:
        """
        获取对话的所有消息
        """
        return self.db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).all()

    async def process_chat_message(self, chat_request: ChatRequest, user_id: Optional[int] = None) -> ChatResponse:
        """
        处理聊天消息并返回AI回复
        """
        # 创建或获取对话
        if not chat_request.conversation_id:
            conversation = self.create_conversation(
                ConversationCreate(title=chat_request.message[:50] + "..."),
                user_id
            )
            chat_request.conversation_id = conversation.id
        else:
            conversation = self.get_conversation(chat_request.conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")

        # 添加用户消息
        user_message = self.add_message(MessageCreate(
            conversation_id=chat_request.conversation_id,
            role="user",
            content=chat_request.message,
            message_type=chat_request.message_type,
            media_url=chat_request.media_url
        ))

        # 构建消息历史
        messages = self.get_conversation_messages(chat_request.conversation_id)
        message_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        # 处理多模态消息
        if chat_request.message_type == "image" and chat_request.media_url:
            # 图像分析
            analysis_result = await llm_service.analyze_image(
                chat_request.media_url,
                "Analyze this image and respond to the user's question: " + chat_request.message
            )
            response_content = analysis_result["analysis"]
        elif chat_request.message_type == "audio" and chat_request.media_url:
            # 音频转录
            transcription_result = await llm_service.transcribe_audio(chat_request.media_url)
            response_content = f"Transcribed: {transcription_result['text']}"
        else:
            # 文本对话
            llm_response = await llm_service.chat_completion(
                messages=message_history,
                model=chat_request.model,
                max_tokens=chat_request.max_tokens,
                temperature=chat_request.temperature
            )
            response_content = llm_response["content"]

        # 添加AI回复消息
        ai_message = self.add_message(MessageCreate(
            conversation_id=chat_request.conversation_id,
            role="assistant",
            content=response_content,
            message_type="text"
        ))

        return ChatResponse(
            response=response_content,
            conversation_id=chat_request.conversation_id,
            message_id=ai_message.id,
            model_used=chat_request.model,
            tokens_used=llm_response.get("tokens_used") if "tokens_used" in llm_response else None
        )

    def delete_conversation(self, conversation_id: int) -> bool:
        """
        删除对话
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            # 删除相关消息
            self.db.query(Message).filter(Message.conversation_id == conversation_id).delete()
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False

    def update_conversation_title(self, conversation_id: int, title: str) -> Optional[Conversation]:
        """
        更新对话标题
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(conversation)
        return conversation