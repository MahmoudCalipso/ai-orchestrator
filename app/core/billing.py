"""Token usage tracking and budget enforcement."""
import logging
from datetime import datetime
from typing import Dict
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class TokenBudgetManager:
    """Manages and enforces token budgets using Redis."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_budget = 100000  # Default 100k tokens per day
        
    async def check_budget(self, user_id: str, estimated_tokens: int) -> bool:
        """Verifies if the user has enough remaining budget for a request."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"usage:{user_id}:{today}"
        
        try:
            current_raw = await self.redis.get(key)
            current = int(current_raw or 0)
            
            if (current + estimated_tokens) > self.default_budget:
                logger.warning(f"User {user_id} exceeded token budget: {current} + {estimated_tokens} > {self.default_budget}")
                return False
            return True
        except Exception as e:
            logger.error(f"Error checking budget for user {user_id}: {e}")
            # Fail-open in case of Redis issues? Or fail-closed for security?
            # Prefer fail-open for UX unless strict billing is required.
            return True
    
    async def record_usage(self, user_id: str, input_tokens: int, output_tokens: int):
        """Updates the user's daily token usage in Redis."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"usage:{user_id}:{today}"
        total = input_tokens + output_tokens
        
        try:
            pipe = self.redis.pipeline()
            pipe.incrby(key, total)
            # Expire after 7 days to keep Redis clean
            pipe.expire(key, 86400 * 7)
            await pipe.execute()
            logger.info(f"Recorded {total} tokens for user {user_id}")
        except Exception as e:
            logger.error(f"Error recording usage for user {user_id}: {e}")
    
    async def get_usage(self, user_id: str) -> Dict:
        """Retrieves usage statistics for a user."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        key = f"usage:{user_id}:{today}"
        
        try:
            current_raw = await self.redis.get(key)
            current = int(current_raw or 0)
            return {
                "daily_usage": current,
                "daily_limit": self.default_budget,
                "remaining": max(0, self.default_budget - current),
                "period": today
            }
        except Exception as e:
            logger.error(f"Error getting usage for user {user_id}: {e}")
            return {
                "daily_usage": 0,
                "daily_limit": self.default_budget,
                "remaining": self.default_budget,
                "error": "Failed to retrieve usage data"
            }
