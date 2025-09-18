import numpy as np
import faiss
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from ..models.models import Memory, DocumentChunk, WorkingMemory
from ..core.config import settings
import json

class VectorService:
    def __init__(self):
        # 初始化embedding模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # all-MiniLM-L6-v2的维度

        # 创建向量存储目录
        self.vector_store_dir = os.path.join(settings.upload_dir, "vector_store")
        os.makedirs(self.vector_store_dir, exist_ok=True)

        # 初始化FAISS索引
        self.memory_index = None
        self.document_index = None
        self._init_indices()

    def _init_indices(self):
        """初始化FAISS索引"""
        # 记忆向量索引
        memory_index_path = os.path.join(self.vector_store_dir, "memory_index.faiss")
        if os.path.exists(memory_index_path):
            self.memory_index = faiss.read_index(memory_index_path)
        else:
            self.memory_index = faiss.IndexFlatIP(self.embedding_dim)  # 内积相似度

        # 文档向量索引
        document_index_path = os.path.join(self.vector_store_dir, "document_index.faiss")
        if os.path.exists(document_index_path):
            self.document_index = faiss.read_index(document_index_path)
        else:
            self.document_index = faiss.IndexFlatIP(self.embedding_dim)

    def text_to_embedding(self, text: str) -> np.ndarray:
        """将文本转换为embedding向量"""
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        # 归一化向量（用于内积相似度计算）
        embedding = embedding / np.linalg.norm(embedding)
        return embedding.astype(np.float32)

    def batch_text_to_embeddings(self, texts: List[str]) -> np.ndarray:
        """批量将文本转换为embedding向量"""
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        # 归一化向量
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        return embeddings.astype(np.float32)

    def save_indices(self):
        """保存FAISS索引到文件"""
        memory_index_path = os.path.join(self.vector_store_dir, "memory_index.faiss")
        document_index_path = os.path.join(self.vector_store_dir, "document_index.faiss")

        faiss.write_index(self.memory_index, memory_index_path)
        faiss.write_index(self.document_index, document_index_path)

    def add_memory_embedding(self, memory_id: int, content: str, db: Session):
        """添加记忆到向量索引"""
        try:
            embedding = self.text_to_embedding(content)

            # 添加到FAISS索引
            self.memory_index.add(embedding.reshape(1, -1))

            # 保存ID映射
            self._save_id_mapping("memory", memory_id, self.memory_index.ntotal - 1)

            # 更新数据库中的embedding
            memory = db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.embedding = pickle.dumps(embedding)
                db.commit()

            self.save_indices()

        except Exception as e:
            print(f"Error adding memory embedding: {e}")

    def add_document_chunk_embedding(self, chunk_id: int, content: str, db: Session):
        """添加文档块到向量索引"""
        try:
            embedding = self.text_to_embedding(content)

            # 添加到FAISS索引
            self.document_index.add(embedding.reshape(1, -1))

            # 保存ID映射
            self._save_id_mapping("document", chunk_id, self.document_index.ntotal - 1)

            # 更新数据库中的embedding
            chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
            if chunk:
                chunk.embedding = pickle.dumps(embedding)
                db.commit()

            self.save_indices()

        except Exception as e:
            print(f"Error adding document chunk embedding: {e}")

    def _save_id_mapping(self, index_type: str, item_id: int, vector_index: int):
        """保存ID映射关系"""
        mapping_file = os.path.join(self.vector_store_dir, f"{index_type}_id_mapping.json")

        mapping = {}
        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)

        mapping[str(vector_index)] = item_id

        with open(mapping_file, 'w') as f:
            json.dump(mapping, f)

    def _load_id_mapping(self, index_type: str) -> Dict[int, int]:
        """加载ID映射关系"""
        mapping_file = os.path.join(self.vector_store_dir, f"{index_type}_id_mapping.json")

        if os.path.exists(mapping_file):
            with open(mapping_file, 'r') as f:
                return {int(k): v for k, v in json.load(f).items()}

        return {}

    def search_similar_memories(self, query: str, limit: int = 10, threshold: float = 0.7,
                               user_id: Optional[int] = None, memory_type: Optional[str] = None,
                               db: Session = None) -> List[Dict[str, Any]]:
        """搜索相似记忆"""
        try:
            query_embedding = self.text_to_embedding(query)

            # 在FAISS中搜索
            distances, indices = self.memory_index.search(query_embedding.reshape(1, -1), limit)

            results = []
            memory_mapping = self._load_id_mapping("memory")

            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1 or distance < threshold:
                    continue

                memory_id = memory_mapping.get(idx)
                if not memory_id:
                    continue

                # 从数据库获取记忆详情
                if db:
                    memory = db.query(Memory).filter(Memory.id == memory_id).first()
                    if memory:
                        # 过滤条件
                        if user_id and memory.user_id != user_id:
                            continue
                        if memory_type and memory.memory_type != memory_type:
                            continue

                        results.append({
                            "id": memory.id,
                            "content": memory.content,
                            "memory_type": memory.memory_type,
                            "importance_score": memory.importance_score,
                            "score": float(distance),
                            "created_at": memory.created_at.isoformat(),
                            "metadata": memory.metadata
                        })

            return sorted(results, key=lambda x: x["score"], reverse=True)

        except Exception as e:
            print(f"Error searching memories: {e}")
            return []

    def search_similar_documents(self, query: str, limit: int = 5, threshold: float = 0.7,
                                knowledge_base_ids: Optional[List[int]] = None,
                                db: Session = None) -> List[Dict[str, Any]]:
        """搜索相似文档"""
        try:
            query_embedding = self.text_to_embedding(query)

            # 在FAISS中搜索
            distances, indices = self.document_index.search(query_embedding.reshape(1, -1), limit)

            results = []
            document_mapping = self._load_id_mapping("document")

            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1 or distance < threshold:
                    continue

                chunk_id = document_mapping.get(idx)
                if not chunk_id:
                    continue

                # 从数据库获取文档块详情
                if db:
                    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
                    if chunk:
                        # 过滤知识库
                        if knowledge_base_ids and chunk.document.knowledge_base_id not in knowledge_base_ids:
                            continue

                        results.append({
                            "id": chunk.id,
                            "content": chunk.content,
                            "document_id": chunk.document_id,
                            "chunk_index": chunk.chunk_index,
                            "score": float(distance),
                            "metadata": chunk.metadata,
                            "document_name": chunk.document.original_name
                        })

            return sorted(results, key=lambda x: x["score"], reverse=True)

        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本之间的相似度"""
        try:
            embedding1 = self.text_to_embedding(text1)
            embedding2 = self.text_to_embedding(text2)

            # 计算余弦相似度
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def update_memory_importance(self, memory_id: int, importance_score: float, db: Session):
        """更新记忆的重要性分数"""
        try:
            memory = db.query(Memory).filter(Memory.id == memory_id).first()
            if memory:
                memory.importance_score = importance_score
                memory.last_accessed = datetime.utcnow()
                memory.access_count += 1
                db.commit()
        except Exception as e:
            print(f"Error updating memory importance: {e}")

    def cleanup_old_memories(self, db: Session, days_threshold: int = 30):
        """清理旧的记忆"""
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)

            # 获取低重要性的旧记忆
            old_memories = db.query(Memory).filter(
                Memory.created_at < cutoff_date,
                Memory.importance_score < 0.3
            ).all()

            for memory in old_memories:
                # 从数据库删除
                db.delete(memory)

            db.commit()

            # 重建索引（简化版本，生产环境需要更复杂的处理）
            self._rebuild_memory_index(db)

            print(f"Cleaned up {len(old_memories)} old memories")

        except Exception as e:
            print(f"Error cleaning up old memories: {e}")

    def _rebuild_memory_index(self, db: Session):
        """重建记忆索引"""
        try:
            # 重新初始化索引
            self.memory_index = faiss.IndexFlatIP(self.embedding_dim)

            # 重新添加所有记忆
            memories = db.query(Memory).filter(Memory.embedding.isnot(None)).all()

            for memory in memories:
                if memory.embedding:
                    embedding = pickle.loads(memory.embedding)
                    self.memory_index.add(embedding.reshape(1, -1))

            self.save_indices()

        except Exception as e:
            print(f"Error rebuilding memory index: {e}")

# 全局向量服务实例
vector_service = VectorService()