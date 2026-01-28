"""Distributed Redis caching service."""
from redis.asyncio import Redis
from typing import Optional, Any, Callable
import json
import pickle
import logging
import hashlib
from functools import wraps

logger = logging.getLogger(__name__)

class CacheService:
    """Provides high-performance caching via Redis."""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Retrieves a value from cache, attempting JSON then Pickle decoding."""
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value)
                except Exception:
                    logger.error(f"Failed to decode cache key: {key}")
                    return None
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Stores a value in cache, serializing as JSON if possible, otherwise Pickle."""
        ttl = ttl or self.default_ttl
        try:
            serialized = json.dumps(value)
        except (TypeError, OverflowError):
            serialized = pickle.dumps(value)
            
        await self.redis.setex(key, ttl, serialized)
    
    async def delete(self, key: str):
        """Removes a specific key from cache."""
        await self.redis.delete(key)
    
    async def delete_pattern(self, pattern: str):
        """Removes all keys matching a pattern."""
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    def cached(
        self, 
        key_prefix: str, 
        ttl: Optional[int] = None,
        key_builder: Optional[Callable] = None
    ):
        """Decorator for caching async function results."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    # Default: prefix + hash of args
                    args_str = str(args) + str(sorted(kwargs.items()))
                    hash_key = hashlib.md5(args_str.encode()).hexdigest()
                    cache_key = f"{key_prefix}:{hash_key}"
                
                # Check cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute and store
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
