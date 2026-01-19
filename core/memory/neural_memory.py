"""
Neural Memory Manager - Hybrid Memory System for 2026
L1: In-Memory (Fast)
L2: SQLite (Persistent Metadata & Context)
L3: Vector Store (Semantic Indexing - Placeholder)
"""
import logging
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from core.memory import MemoryManager

logger = logging.getLogger(__name__)

class NeuralMemoryManager(MemoryManager):
    """Enhanced memory manager with persistent L2 storage"""
    
    def __init__(self, db_path: str = "data/memory.db", max_entries: int = 2000):
        super().__init__(max_entries=max_entries)
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        from core.memory.vector_store import VectorStoreService
        self.vector_store = VectorStoreService()

    def _init_db(self):
        """Initialize SQLite L2 storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tags ON interactions(tags)")
            conn.commit()

    async def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern"""
        return await super().get_keys(pattern)

    async def search_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        L3 Vector Store Indexing.
        Uses ChromaDB for deep codebase awareness.
        """
        logger.info(f"Neural Memory: Performing deep semantic search for '{query}'")
        
        # Query ChromaDB
        results = self.vector_store.query_semantic(query, limit=limit)
        
        # If no results from vector store, fall back to keyword matching
        if not results:
            logger.info("No vector results, falling back to keyword matching")
            keywords = query.lower().split()
            for kw in keywords[:3]: 
                tag_results = await self.search_by_tag(kw)
                results.extend(tag_results)
            
        return results[:limit]

    async def store(self, key: str, value: Any, tags: List[str] = None, ttl: Optional[int] = None):
        """Store in L1 and L2"""
        # L1 (Current session ram)
        await super().store(key, value, ttl)
        
        # L2 (SQLite Persistence)
        try:
            with sqlite3.connect(self.db_path) as conn:
                value_json = json.dumps(value)
                tags_json = json.dumps(tags or [])
                conn.execute("""
                    INSERT OR REPLACE INTO interactions (key, value, tags, last_access)
                    VALUES (?, ?, ?, ?)
                """, (key, value_json, tags_json, datetime.now()))
                conn.commit()
        except Exception as e:
            logger.error(f"L2 Storage failed for key {key}: {e}")

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from L1 (fast) or L2 (persistent)"""
        # Try L1 first
        val = await super().retrieve(key)
        if val:
            return val
            
        # Try L2
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value FROM interactions WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    # Populate back to L1 for faster subsequent access
                    await super().store(key, data)
                    return data
        except Exception as e:
            logger.error(f"L2 Retrieval failed for key {key}: {e}")
            
        return None

    async def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Find relevant context by technical tags"""
        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Simple JSON tag search
                cursor = conn.execute("SELECT key, value FROM interactions WHERE tags LIKE ?", (f'%"{tag}"%',))
                for row in cursor.fetchall():
                    results.append({"key": row[0], "value": json.loads(row[1])})
        except Exception as e:
            logger.error(f"L2 Tag search failed for {tag}: {e}")
        return results
