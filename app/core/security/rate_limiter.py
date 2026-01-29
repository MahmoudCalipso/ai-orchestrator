"""Redis-backed sliding window rate limiter."""
import time
import logging
import json
from typing import Tuple, Dict, Any
import redis.asyncio as redis
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class RateLimiter:
    """Sliding window rate limiter with Redis-backed persistence."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        # Thresholds from V2.0 Spec
        self.rpm_limit = 60
        self.daily_token_limit = 100000 
        
    async def check(self, user_id: str, estimated_tokens: int = 0) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifies if the user is within their rate and token limits.
        Uses a sliding window for RPM and a daily counter for tokens.
        """
        now = time.time()
        minute_ago = now - 60
        day_key = f"rl:tokens:{user_id}:{time.strftime('%Y-%m-%d')}"
        window_key = f"rl:window:{user_id}"
        
        try:
            # 1. Check RPM (Sliding Window via Sorted Set)
            pipe = self.redis.pipeline()
            # Remove old requests
            pipe.zremrangebyscore(window_key, 0, minute_ago)
            # Add current request
            pipe.zadd(window_key, {str(now): now})
            # Count requests in the last minute
            pipe.zcard(window_key)
            # Set expiry for the window key
            pipe.expire(window_key, 60)
            
            # Execute RPM check
            _, _, request_count, _ = await pipe.execute()
            
            if request_count > self.rpm_limit:
                logger.warning(f"Rate limit exceeded for user {user_id}: {request_count} rpm")
                return False, {"reason": "rate_limit_exceeded", "limit": self.rpm_limit, "current": request_count}
            
            # 2. Check Token Budget (Daily limit)
            if estimated_tokens > 0:
                current_daily_tokens = await self.redis.incrby(day_key, estimated_tokens)
                if current_daily_tokens == estimated_tokens:
                    # First request of the day, set expiry
                    await self.redis.expire(day_key, 86400)
                
                if current_daily_tokens > self.daily_token_limit:
                    logger.warning(f"Token budget exceeded for user {user_id}: {current_daily_tokens} tokens")
                    return False, {"reason": "token_budget_exceeded", "limit": self.daily_token_limit, "current": current_daily_tokens}
            
            return True, {"status": "ok", "rpm": request_count}
            
        except Exception as e:
            logger.error(f"Rate limiter error for user {user_id}: {e}")
            # Fail open to avoid blocking users on cache failure, but log it
            return True, {"status": "degraded", "error": str(e)}

# Note: Global singleton is initialized in main.py lifespan
