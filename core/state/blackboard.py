"""
Blackboard State Store
Centralized state for agent collaboration using Redis
"""
import json
import logging
from typing import Any, Optional, Dict
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class Blackboard:
    """Blackboard pattern implementation for shared agent state"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None

    async def initialize(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Blackboard initialized at {self.redis_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Blackboard: {e}")
            return False

    async def write_knowledge(self, key: str, value: Any, agent_name: str = "system"):
        """Write shared information to the blackboard"""
        if not self.client:
            return
            
        data = {
            "value": value,
            "agent": agent_name,
            "timestamp": None # Could add isoformat timestamp here
        }
        
        await self.client.hset("blackboard:state", key, json.dumps(data))
        logger.debug(f"Blackboard: '{agent_name}' wrote to '{key}'")

    async def read_knowledge(self, key: str) -> Optional[Any]:
        """Read information from the blackboard"""
        if not self.client:
            return None
            
        raw = await self.client.hget("blackboard:state", key)
        if raw:
            data = json.loads(raw)
            return data.get("value")
        return None

    async def get_all_knowledge(self) -> Dict[str, Any]:
        """Fetch all shared knowledge"""
        if not self.client:
            return {}
            
        all_raw = await self.client.hgetall("blackboard:state")
        return {k: json.loads(v).get("value") for k, v in all_raw.items()}

    async def clear(self):
        """Wipe the blackboard"""
        if self.client:
            await self.client.delete("blackboard:state")
