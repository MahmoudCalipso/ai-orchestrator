"""
Neural Memory Manager - Hybrid Memory System for 2026
L0: Redis (Hot Cache)
L1: PostgreSQL (Persistent Context & Patterns)
L2: Qdrant (Semantic Indexing)
"""
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import select, update, delete

from core.memory import MemoryManager
from core.database.manager import unified_db
from core.database.models import NeuralMemory

logger = logging.getLogger(__name__)

class NeuralMemoryManager(MemoryManager):
    """
    Enhanced memory manager with:
    - Redis (L0) for microsecond retrieval of active context.
    - PostgreSQL (L1) for transactional persistence.
    - Qdrant (L2) for semantic search.
    """
    
    def __init__(self, max_entries: int = 2000):
        super().__init__(max_entries=max_entries)
        # Vector store will be refactored to use Qdrant in VectorStoreService
        from core.memory.vector_store import VectorStoreService
        self.vector_store = VectorStoreService()
        self.cache_ttl = 604800  # 7 days

    async def store(self, key: str, value: Any, tags: List[str] = None, ttl: Optional[int] = None):
        """Store in L0 (Redis) and L1 (Postgres)"""
        
        # 1. Hot Cache (Redis L0)
        try:
            cache_data = {
                "content": value,
                "tags": tags or [],
                "stored_at": datetime.now().isoformat()
            }
            await unified_db.redis.set(
                f"nm:hot:{key}", 
                json.dumps(cache_data), 
                ex=ttl or self.cache_ttl
            )
        except Exception as e:
            logger.error(f"Redis Storage failed for key {key}: {e}")

        # 2. Persistence (Postgres L1)
        try:
            async with unified_db.AsyncSessionLocal() as session:
                # Check if exists
                stmt = select(NeuralMemory).where(NeuralMemory.memory_type == key)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    existing.content = value
                    existing.accessed_count += 1
                else:
                    new_mem = NeuralMemory(
                        memory_type=key, # Using key as memory_type or identifier
                        content=value,
                        confidence_score=1.0
                    )
                    session.add(new_mem)
                
                await session.commit()
        except Exception as e:
            logger.error(f"Postgres Storage failed for key {key}: {e}")

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve from L0 (Redis) or fallback to L1 (Postgres)"""
        
        # 1. Try Redis (L0)
        try:
            cached = await unified_db.redis.get(f"nm:hot:{key}")
            if cached:
                data = json.loads(cached)
                return data["content"]
        except Exception as e:
            logger.error(f"Redis Retrieval failed for key {key}: {e}")

        # 2. Try Postgres (L1)
        try:
            async with unified_db.AsyncSessionLocal() as session:
                stmt = select(NeuralMemory).where(NeuralMemory.memory_type == key)
                result = await session.execute(stmt)
                mem = result.scalar_one_or_none()
                
                if mem:
                    # Update accessed count
                    mem.accessed_count += 1
                    await session.commit()
                    
                    # Back-populate Redis for next time
                    await unified_db.redis.set(
                        f"nm:hot:{key}", 
                        json.dumps({"content": mem.content, "stored_at": datetime.now().isoformat()}),
                        ex=self.cache_ttl
                    )
                    return mem.content
        except Exception as e:
            logger.error(f"Postgres Retrieval failed for key {key}: {e}")

        return None

    async def search_semantic(self, query: str, orchestrator: Any, limit: int = 5) -> List[Dict[str, Any]]:
        """L2 Vector Store Indexing (Qdrant)"""
        logger.info(f"Neural Memory: Performing deep semantic search for '{query}'")
        return await self.vector_store.query_semantic(query, orchestrator, limit=limit)

    async def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Find relevant context by technical tags in Postgres"""
        results = []
        try:
            async with unified_db.AsyncSessionLocal() as session:
                # PostgreSQL JSONB search
                stmt = select(NeuralMemory).where(NeuralMemory.content.cast(String).like(f'%{tag}%'))
                result = await session.execute(stmt)
                mems = result.scalars().all()
                for item in mems:
                    results.append({"key": item.memory_type, "value": item.content})
        except Exception as e:
            logger.error(f"Postgres Tag search failed for {tag}: {e}")
        return results
