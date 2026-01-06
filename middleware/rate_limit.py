"""
Advanced Rate Limiting
"""
from fastapi import Request, HTTPException
from time import time
import asyncio

class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.cleanup_task = None

    async def check_rate_limit(
            self,
            request: Request,
            max_requests: int = 100,
            window: int = 60
    ):
        """Check rate limit"""
        client_id = request.headers.get("X-API-Key", "anonymous")
        current_time = time()

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Remove old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < window
        ]

        # Check limit
        if len(self.requests[client_id]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {max_requests} requests per {window} seconds"
            )

        # Add current request
        self.requests[client_id].append(current_time)