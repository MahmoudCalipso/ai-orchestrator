"""
Memory Manager - Manages conversation history and context
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages conversation memory and context"""
    
    def __init__(self, max_entries: int = 1000):
        self.memory: Dict[str, Any] = {}
        self.max_entries = max_entries
        self.access_counts: Dict[str, int] = {}
        self.last_access: Dict[str, datetime] = {}
        
    async def initialize(self):
        """Initialize memory manager"""
        logger.info("Memory manager initialized")
        asyncio.create_task(self._cleanup_task())
        
    async def shutdown(self):
        """Shutdown memory manager"""
        logger.info("Memory manager shutting down")
        
    async def store(self, key: str, value: Any, ttl: Optional[int] = None):
        self.memory[key] = {
            "value": value,
            "created_at": datetime.now(),
            "ttl": ttl,
            "expires_at": datetime.now() + timedelta(seconds=ttl) if ttl else None
        }
        self.access_counts[key] = 0
        self.last_access[key] = datetime.now()
        if len(self.memory) > self.max_entries:
            await self._evict_lru()
            
    async def retrieve(self, key: str) -> Optional[Any]:
        if key not in self.memory: return None
        entry = self.memory[key]
        if entry["expires_at"] and datetime.now() > entry["expires_at"]:
            del self.memory[key]
            return None
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        self.last_access[key] = datetime.now()
        return entry["value"]
        
    async def delete(self, key: str):
        if key in self.memory: del self.memory[key]
        if key in self.access_counts: del self.access_counts[key]
        if key in self.last_access: del self.last_access[key]
        
    async def clear(self):
        self.memory.clear()
        self.access_counts.clear()
        self.last_access.clear()
        
    async def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        if pattern: return [k for k in self.memory.keys() if pattern in k]
        return list(self.memory.keys())
            
    async def _evict_lru(self):
        if not self.last_access: return
        lru_key = min(self.last_access.items(), key=lambda x: x[1])[0]
        await self.delete(lru_key)
        
    async def _cleanup_task(self):
        while True:
            try:
                await asyncio.sleep(60)
                now = datetime.now()
                expired_keys = [k for k, e in self.memory.items() if e["expires_at"] and now > e["expires_at"]]
                for key in expired_keys: await self.delete(key)
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                
    async def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self.memory),
            "max_entries": self.max_entries,
            "utilization": len(self.memory) / self.max_entries
        }
