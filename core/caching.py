"""
Intelligent Caching System
Implements multi-level caching with Redis backend
"""
import hashlib
import json
import logging
from typing import Any, Optional, Dict
from datetime import timedelta
import pickle

logger = logging.getLogger(__name__)


class CacheManager:
    """Multi-level cache manager with Redis backend"""

    def __init__(self, redis_client=None, enable_memory_cache: bool = True):
        self.redis_client = redis_client
        self.enable_memory_cache = enable_memory_cache
        self.memory_cache: Dict[str, Any] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'redis_hits': 0
        }

    def _generate_key(self, prompt: str, model: str, params: Dict[str, Any]) -> str:
        """Generate cache key from prompt, model, and parameters"""
        cache_data = {
            'prompt': prompt,
            'model': model,
            'params': params
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return f"cache:{hashlib.sha256(cache_str.encode()).hexdigest()}"

    async def get(
        self,
        prompt: str,
        model: str,
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        key = self._generate_key(prompt, model, params)

        # Check memory cache first
        if self.enable_memory_cache and key in self.memory_cache:
            self.cache_stats['hits'] += 1
            self.cache_stats['memory_hits'] += 1
            logger.debug(f"Memory cache hit for key: {key[:16]}...")
            return self.memory_cache[key]

        # Check Redis cache
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(key)
                if cached_data:
                    self.cache_stats['hits'] += 1
                    self.cache_stats['redis_hits'] += 1

                    # Deserialize
                    result = pickle.loads(cached_data)

                    # Store in memory cache
                    if self.enable_memory_cache:
                        self.memory_cache[key] = result

                    logger.debug(f"Redis cache hit for key: {key[:16]}...")
                    return result
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        self.cache_stats['misses'] += 1
        return None

    async def set(
        self,
        prompt: str,
        model: str,
        params: Dict[str, Any],
        response: Dict[str, Any],
        ttl: int = 3600
    ):
        """Cache a response"""
        key = self._generate_key(prompt, model, params)

        # Store in memory cache
        if self.enable_memory_cache:
            self.memory_cache[key] = response

            # Limit memory cache size
            if len(self.memory_cache) > 1000:
                # Remove oldest entries
                keys_to_remove = list(self.memory_cache.keys())[:100]
                for k in keys_to_remove:
                    del self.memory_cache[k]

        # Store in Redis
        if self.redis_client:
            try:
                serialized = pickle.dumps(response)
                await self.redis_client.setex(key, ttl, serialized)
                logger.debug(f"Cached response for key: {key[:16]}... (TTL: {ttl}s)")
            except Exception as e:
                logger.error(f"Redis set error: {e}")

    async def invalidate(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            # Clear matching Redis keys
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"cache:{pattern}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                        logger.info(f"Invalidated {len(keys)} Redis cache entries")
                except Exception as e:
                    logger.error(f"Redis invalidation error: {e}")

            # Clear memory cache
            if self.enable_memory_cache:
                keys_to_remove = [
                    k for k in self.memory_cache.keys()
                    if pattern in k
                ]
                for k in keys_to_remove:
                    del self.memory_cache[k]
                logger.info(f"Invalidated {len(keys_to_remove)} memory cache entries")
        else:
            # Clear all
            self.memory_cache.clear()
            if self.redis_client:
                try:
                    await self.redis_client.flushdb()
                    logger.info("Cleared all cache")
                except Exception as e:
                    logger.error(f"Redis flush error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (
            self.cache_stats['hits'] / total_requests * 100
            if total_requests > 0 else 0
        )

        return {
            'total_requests': total_requests,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'memory_hits': self.cache_stats['memory_hits'],
            'redis_hits': self.cache_stats['redis_hits'],
            'memory_cache_size': len(self.memory_cache)
        }

    async def warm_cache(self, common_prompts: list):
        """Pre-warm cache with common prompts"""
        logger.info(f"Warming cache with {len(common_prompts)} prompts")
        # This would be called with actual inference results
        # Implementation depends on your specific needs


class SemanticCache:
    """Semantic similarity-based caching"""

    def __init__(self, embedding_model=None, similarity_threshold: float = 0.95):
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        self.cache = {}

    async def get_embedding(self, text: str):
        """Get embedding for text"""
        # Implement with your embedding model
        # This is a placeholder
        return hashlib.sha256(text.encode()).digest()

    async def find_similar(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Find semantically similar cached response"""
        if not self.embedding_model:
            return None

        # Get embedding for input prompt
        prompt_embedding = await self.get_embedding(prompt)

        # Find most similar cached prompt
        # Implementation would use cosine similarity
        # This is a simplified version

        for cached_prompt, cached_data in self.cache.items():
            # Calculate similarity
            # If similarity > threshold, return cached response
            pass

        return None

    async def store(self, prompt: str, response: Dict[str, Any]):
        """Store with semantic indexing"""
        embedding = await self.get_embedding(prompt)
        self.cache[prompt] = {
            'embedding': embedding,
            'response': response
        }