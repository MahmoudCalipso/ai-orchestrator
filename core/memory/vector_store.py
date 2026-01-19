"""
Vector Store Service - ChromaDB Integration for Semantic RAG
Provides global codebase awareness and semantic search.
"""
import os
import chromadb
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Manages semantic indexing and retrieval using ChromaDB"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VectorStoreService, cls).__new__(cls)
        return cls._instance

    def __init__(self, persist_directory: str = "storage/vector_store"):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Using default embedding function (HuggingFace-based local)
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            self.collection = self.client.get_or_create_collection(
                name="project_context",
                embedding_function=self.embedding_function
            )
            self._initialized = True
            logger.info(f"VectorStoreService initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {e}")
            self._initialized = False

    def index_files(self, files: List[str]):
        """Index a list of absolute file paths into the vector store"""
        if not self._initialized:
            logger.error("VectorStoreService not initialized")
            return

        for file_path in files:
            try:
                if not os.path.exists(file_path) or os.path.isdir(file_path):
                    continue
                
                # Check for binary files or large files to avoid bloat
                if self._is_binary(file_path) or os.path.getsize(file_path) > 1024 * 1024:
                    continue

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue

                # Simple chunking
                chunks = self._chunk_text(content)
                
                ids = [f"{file_path}_{i}" for i in range(len(chunks))]
                metadatas = [{"path": file_path, "chunk": i, "filename": os.path.basename(file_path)} for i in range(len(chunks))]
                
                self.collection.upsert(
                    ids=ids,
                    documents=chunks,
                    metadatas=metadatas
                )
                logger.info(f"Indexed {len(chunks)} chunks from {file_path}")
            except Exception as e:
                logger.error(f"Failed to index {file_path}: {e}")

    def query_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Query the vector store for relevant context"""
        if not self._initialized:
            logger.error("VectorStoreService not initialized")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Semantic query failed: {e}")
            return []

    def clear(self):
        """Clear the entire collection"""
        if self._initialized:
            self.client.delete_collection("project_context")
            self.collection = self.client.get_or_create_collection(
                name="project_context",
                embedding_function=self.embedding_function
            )

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
