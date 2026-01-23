
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.getcwd())

from core.caching import CacheManager
from core.cache_service import cache_service

async def test_caching():
    print("Testing Caching System...")
    
    # 1. Test RedisCacheService (expecting connection failure handled)
    print(f"RedisCacheService status: {'Enabled' if cache_service.redis else 'Disabled'}")
    
    # 2. Test CacheManager (Memory Fallback)
    cache = CacheManager(redis_client=cache_service.redis, enable_memory_cache=True)
    
    prompt = "Hello World"
    model = "gpt-4"
    params = {"temp": 0.7}
    response = {"text": "Hello! How can I help you today?"}
    
    # Set cache
    print("Setting cache entry...")
    await cache.set(prompt, model, params, response)
    
    # Get cache
    print("Retrieving cache entry...")
    cached_result = await cache.get(prompt, model, params)
    
    if cached_result == response:
        print("Success: Memory cache working correctly.")
    else:
        print(f"Failure: Expected {response}, got {cached_result}")
    
    stats = cache.get_stats()
    print(f"Cache Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(test_caching())
