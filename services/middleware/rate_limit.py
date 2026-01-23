"""
Rate Limitation Middleware
Redis-backed distributed rate limiting for API protection
"""
import time
import logging
from typing import Callable, Dict, Optional, Tuple
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.cache_service import cache_service

logger = logging.getLogger(__name__)

# Default rate limits (requests per minute)
TIERS = {
    "free": 10,
    "pro": 100,
    "enterprise": 1000,
    "internal": 10000
}

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits on API requests.
    Uses Redis for distributed counting.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for static files, docs, health checks
        path = request.url.path
        if (path.startswith("/static") or 
            path.startswith("/docs") or 
            path.startswith("/redoc") or 
            path in ["/", "/health", "/status"]):
            return await call_next(request)
            
        # Identify client (API Key or IP)
        client_id, tier = self._identify_client(request)
        
        # Check rate limit
        is_allowed, remaining, reset = await self._check_rate_limit(client_id, tier)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Limit: {TIERS.get(tier, 10)}/min. Try again in {int(reset - time.time())}s"
                },
                headers={
                    "X-RateLimit-Limit": str(TIERS.get(tier, 10)),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(reset))
                }
            )
            
        # Process request
        response = await call_next(request)
        
        # Add headers
        response.headers["X-RateLimit-Limit"] = str(TIERS.get(tier, 10))
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset))
        
        return response

    def _identify_client(self, request: Request) -> Tuple[str, str]:
        """Identify the client and their tier"""
        # 1. Check API Key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            api_key = request.query_params.get("api_key")
            
        if api_key:
            # In production, look up tier in DB/Cache
            # For now, simulate based on key prefix
            if api_key.startswith("sk_ent_"):
                return f"apikey:{api_key}", "enterprise"
            elif api_key.startswith("sk_pro_"):
                return f"apikey:{api_key}", "pro"
            elif api_key.startswith("sk_test_"):
                return f"apikey:{api_key}", "internal"
            return f"apikey:{api_key}", "free"
            
        # 2. Fallback to IP
        ip = request.client.host
        return f"ip:{ip}", "free"

    async def _check_rate_limit(self, client_id: str, tier: str) -> Tuple[bool, int, float]:
        """
        Check if request is allowed.
        Returns: (is_allowed, remaining_requests, reset_time)
        """
        limit = TIERS.get(tier, 10)
        window = 60 # 1 minute
        
        # Current time window
        now = time.time()
        window_start = int(now / window) * window
        key = f"ratelimit:{client_id}:{window_start}"
        
        # If cache service logic fails, fail open (allow request)
        if hasattr(cache_service, 'increment'):
            try:
                # Increment counter
                count = await cache_service.increment(key)
                
                # Set expiry on first request in window
                if count == 1 and cache_service.redis:
                    try:
                        await cache_service.redis.expire(key, window)
                    except:
                        pass # Ignore expiry errors
                    
                remaining = max(0, limit - count)
                reset = window_start + window
                
                # If Redis is disabled (returning 1 always), count will never exceed limit
                return count <= limit, remaining, reset
            except Exception as e:
                logger.error(f"Rate limit verification failed: {e}")
                return True, limit, now + window
                
        # Fallback if Redis unavailable
        return True, limit, now + window
