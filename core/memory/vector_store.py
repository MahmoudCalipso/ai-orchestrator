"""
Vector Store Service - Qdrant Integration for Semantic RAG
Provides global codebase awareness and enterprise-scale semantic search.
"""
import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from qdrant_client.models import PointStruct, VectorParams, Distance

from core.database.manager import unified_db

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Manages semantic indexing and retrieval using Qdrant"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
        return cls._instance

    def __init__(self, collection_name: str = "project_context"):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.collection_name = collection_name
        self._initialized = False
        
        # We need the orchestrator for embeddings
        # But we'll initialize it lazily or use a placeholder until available
        self._orchestrator = None

    async def ensure_collection(self, vector_size: int = 1536):
        """Ensure the target collection exists in Qdrant"""
        try:
            collections = await unified_db.qdrant.get_collections()
            exist = any(c.name == self.collection_name for c in collections.collections)
            
            if not exist:
                await unified_db.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection: {e}")

    async def index_files(self, files: List[str], orchestrator: Any):
        """Index a list of absolute file paths into Qdrant"""
        await self.ensure_collection()
        
        points = []
        for file_path in files:
            try:
                if not os.path.exists(file_path) or os.path.isdir(file_path):
                    continue
                
                if self._is_binary(file_path) or os.path.getsize(file_path) > 1024 * 1024:
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue

                chunks = self._chunk_text(content)
                
                for i, chunk in enumerate(chunks):
                    # Generate embedding via LLM Engine
                    embedding = await orchestrator.llm.get_embeddings(chunk)
                    
                    # Create Qdrant Point
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{file_path}_{i}"))
                    points.append(PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "path": file_path,
                            "filename": os.path.basename(file_path),
                            "content": chunk,
                            "chunk_index": i
                        }
                    ))
                
                if points:
                    await unified_db.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.info(f"Indexed {len(points)} chunks from {file_path} to Qdrant")
                    points = [] # Clear for next file
            except Exception as e:
                logger.error(f"Failed to index {file_path} to Qdrant: {e}")

    async def query_semantic(self, query: str, orchestrator: Any, limit: int = 5) -> List[Dict[str, Any]]:
        """Query Qdrant for relevant context"""
        await self.ensure_collection()
        
        try:
            # Generate search embedding
            query_vector = await orchestrator.llm.get_embeddings(query)
            
            search_result = await unified_db.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            formatted_results = []
            for hit in search_result:
                formatted_results.append({
                    "content": hit.payload.get("content", ""),
                    "metadata": {
                        "path": hit.payload.get("path"),
                        "filename": hit.payload.get("filename"),
                        "chunk": hit.payload.get("chunk_index")
                    },
                    "score": hit.score
                })
            return formatted_results
        except Exception as e:
            logger.error(f"Qdrant Semantic query failed: {e}")
            return []

    def _chunk_text(self, text: str, chunk_size: int = 1500, overlap: int = 300) -> List[str]:
        """Simple text chunking with overlap"""
        chunks = []
        if not text:
            return chunks
        
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start += chunk_size - overlap
            
        return chunks

    def _is_binary(self, file_path: str) -> bool:
        """Simple check if a file is binary"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\x00' in chunk
        except:
            return True
