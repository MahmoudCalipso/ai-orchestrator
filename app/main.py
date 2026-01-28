"""Main FastAPI application entry point."""
import logging
import os
import uuid
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .core.database import db_manager
from .core.agent_manager import agent_manager
from .core.container import setup_container
from .core.exceptions import global_exception_handler, BaseAppException
import redis.asyncio as redis
from .core.billing import TokenBudgetManager
from .middleware.auth import JWTBearer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core instances that will be shared across the app
redis_client = None
budget_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application."""
    logger.info("Initializing AI Orchestrator Backend...")
    
    # Setup Dependency Injection Container
    container = setup_container()
    app.state.container = container
    
    # Initialize Database & Create Tables
    db_manager.initialize()
    await db_manager.create_tables()
    
    # Initialize Redis & Token Budgeting
    global redis_client, budget_manager
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = await redis.from_url(redis_url)
    budget_manager = TokenBudgetManager(redis_client)
    
    # Start Agent Lifecycle Manager
    await agent_manager.start()
    
    logger.info("AI Orchestrator Backend ready")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down AI Orchestrator Backend...")
    await agent_manager.stop()
    await db_manager.close()
    if redis_client:
        await redis_client.close()
    logger.info("Shutdown complete")

# Create FastAPI instance with premium documentation settings
app = FastAPI(
    title="🚀 AI Orchestrator Control Plane",
    description="Ultimate AI Agent OS for Production-Ready Scalability",
    version="2026.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response: Response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Register Global Exception Handlers
app.add_exception_handler(BaseAppException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2026.1.0"}

# Include Routers (v1)
from .api.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
