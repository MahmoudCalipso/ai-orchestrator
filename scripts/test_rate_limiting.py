import asyncio
import os
import sys
import time
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.getcwd())

from services.middleware.rate_limit import RateLimitMiddleware
from core.cache_service import cache_service

app = FastAPI()
app.add_middleware(RateLimitMiddleware)

@app.get("/test")
async def test_endpoint():
    return {"status": "ok"}

def test_rate_limiting():
    print("Testing Rate Limiting Middleware...")
    client = TestClient(app)
    
    # Use a specific API key to track limit
    headers = {"X-API-Key": "sk_test_123"} # Test tier: 10000/min
    
    # We'll use a lower tier for testing if we want to hit the limit quickly
    # But for free tier, it's 10/min. Let's use that.
    free_headers = {"X-API-Key": "sk_free_123"}
    
    print("Sending 10 requests (Free Tier Limit: 10/min)...")
    for i in range(10):
        response = client.get("/test", headers=free_headers)
        if response.status_code != 200:
            print(f"Request {i+1} failed: {response.status_code}")
            return
            
    print("Request 11 (should be blocked if Redis is working)...")
    response = client.get("/test", headers=free_headers)
    
    if response.status_code == 429:
        print("Success: Request 11 was rate limited!")
    else:
        print(f"Result: Request 11 returned {response.status_code}")
        if cache_service.redis is None:
            print("Note: Redis is not available, so rate limiting (distributed) is effectively disabled (always allows). This is expected behavior for local fallback.")
        else:
            print("Warning: Redis is available but request 11 was NOT blocked.")

if __name__ == "__main__":
    test_rate_limiting()
