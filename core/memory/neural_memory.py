"""
Neural Memory Manager - Hybrid Memory System for 2026
L1: In-Memory (Fast)
L2: SQLite (Persistent Metadata & Context)
L3: Vector Store (Semantic Indexing - Placeholder)
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, DateTime, Text, select, insert, delete
from sqlalchemy.orm import Session
from core.memory import MemoryManager
from platform_core.database import Base, engine, SessionLocal

logger = logging.getLogger(__name__)

class Interaction(Base):
    """Memory interaction model for persistence"""
    __tablename__ = "interactions"
    key = Column(String, primary_key=True)
    value = Column(Text)
    tags = Column(Text) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    last_access = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Ensure table exists
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

class NeuralMemoryManager(MemoryManager):
    """Enhanced memory manager with persistent SQLAlchemy storage"""
    
    def __init__(self, max_entries: int = 2000):
        super().__init__(max_entries=max_entries)
        from core.memory.vector_store import VectorStoreService
        self.vector_store = VectorStoreService()

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
        """Store in L1 and DB"""
        # L1 (Current session ram)
        await super().store(key, value, ttl)
        
        # DB Persistence (PostgreSQL/SQLite)
        try:
            with SessionLocal() as db:
                value_json = json.dumps(value)
                tags_json = json.dumps(tags or [])
                
                existing = db.query(Interaction).filter(Interaction.key == key).first()
                if existing:
                    existing.value = value_json
                    existing.tags = tags_json
                    existing.last_access = datetime.utcnow()
                else:
                    new_interaction = Interaction(
                        key=key,
                        value=value_json,
                        tags=tags_json
                    )
                    db.add(new_interaction)
                db.commit()
        except Exception as e:
            logger.error(f"DB Storage failed for key {key}: {e}")

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from L1 (fast) or DB (persistent)"""
        # Try L1 first
        val = await super().retrieve(key)
        if val:
            return val
            
        # Try DB
        try:
            with SessionLocal() as db:
                interaction = db.query(Interaction).filter(Interaction.key == key).first()
                if interaction:
                    data = json.loads(interaction.value)
                    # Populate back to L1 for faster subsequent access
                    await super().store(key, data)
                    return data
        except Exception as e:
            logger.error(f"DB Retrieval failed for key {key}: {e}")
            
        return None

    async def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Find relevant context by technical tags"""
        results = []
        try:
            with SessionLocal() as db:
                # Simple string contains search for tags
                interactions = db.query(Interaction).filter(Interaction.tags.like(f'%"{tag}"%')).all()
                for item in interactions:
                    results.append({"key": item.key, "value": json.loads(item.value)})
        except Exception as e:
            logger.error(f"DB Tag search failed for {tag}: {e}")
        return results
