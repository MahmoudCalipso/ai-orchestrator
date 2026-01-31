"""Main FastAPI application entry point."""
import logging
import os
import asyncio
import uuid
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .core.database import db_manager
from .core.agent_manager import agent_manager
from .core.container import setup_container, container
from .models import all as models_registry
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
    logger.info("🚀 IA-ORCH: Starting Production Control Plane (v2026.2.0)")
    
    # 1. Setup Dependency Injection
    setup_container()
    app.state.container = container
    
    # 2. Database & Agent Initialization
    container.db_manager().initialize()
    await container.db_manager().create_tables()
    await container.agent_manager().start()
    
    # 3. Start Background Workers
    await container.message_bus().start()
    await container.monitoring_service().start()
    
    # 4. Schedule Registry Updates
    from services.registry.registry_updater import RegistryUpdater
    updater = RegistryUpdater()
    asyncio.create_task(updater.schedule_periodic_updates(interval_hours=24))
    
    logger.info("✓ AI Orchestrator Backend ready - All systems GO")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down IA-ORCH Services...")
    await container.agent_manager().stop()
    await container.message_bus().stop() # Assuming stop exists
    await container.monitoring_service().stop()
    await container.db_manager().close()
    logger.info("✓ Shutdown complete")

# Premium Documentation Metadata
API_DESCRIPTION = """
# 🚀 AI Orchestrator Control Plane
### The Ultimate AI Agent OS for Production-Ready Scalability

Welcome to the unified nerve center of the **AI Orchestrator**. 
- **Swarm Intelligence**: Autonomous agent coordination.
- **Post-Quantum Security**: Quantum-ready vault protection.
- **Closed-Loop Healing**: Self-patching infrastructure.
"""

# Tags Metadata for clean grouping
tags_metadata = [
    {
        "name": "Core Intelligence",
        "description": "Primary Swarm Access Points for Generation, Migration, and Analysis.",
    },
    {
        "name": "Project Lifecycle", 
        "description": "Standard Async CRUD for Project Management.",
    },
    {
        "name": "Git Ops",
        "description": "Bi-directional repository synchronization and conflict resolution.",
    },
    {
        "name": "System Health",
        "description": "Real-time telemetry and resource monitoring.",
    },
    {
        "name": "WebSocket Streaming",
        "description": "Real-time log streaming and interactive terminal sessions via `ws://` protocol.",
        "externalDocs": {
            "description": "WebSocket Protocol Specs",
            "url": "https://fastapi.tiangolo.com/advanced/websockets/",
        },
    },
]

# Create FastAPI instance with premium documentation settings
app = FastAPI(
    title="🚀 AI Orchestrator Control Plane",
    description=API_DESCRIPTION,
    version="2026.2.0-v2",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,   # Show Schemas section
        "docExpansion": "list",          # Expand tags, collapse operations
        "filter": True,                  # Enable search bar
        "syntaxHighlight.theme": "monokai", # Premium coding feel
        "persistAuthorization": True,    # Keep auth token on refresh
        "displayRequestDuration": True,  # Show latency
        "tryItOutEnabled": True,         # Ready to click
    }
)

# --- Root Redirect ---
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to Swagger UI"""
    return RedirectResponse(url="/docs")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
from .core.exceptions import global_exception_handler, BaseAppException
app.add_exception_handler(BaseAppException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# --- Standard Health Probes ---
@app.get("/health")
async def health_check():
    """Enterprise health check with sub-system metrics."""
    db_metrics = container.db_manager().get_pool_status()
    return {
        "status": "healthy", 
        "version": "2026.2.0-v2",
        "database": {"pool": db_metrics},
        "system": {"environment": os.getenv("APP_ENV", "dev")}
    }

@app.get("/health/live")
async def live_check(): return {"status": "alive"}

@app.get("/health/ready")
async def ready_check():
    db_metrics = container.db_manager().get_pool_status()
    if db_metrics.get("saturation", 0) > 90:
         raise HTTPException(status_code=503, detail="Database pool saturated")
    return {"status": "ready"}

# Include Routers (Consolidated v1)
from .controllers.v1.api import api_router
app.include_router(api_router, prefix="/api/v1")

# WebSocket Layer
from .controllers.ws.websocket_controller import router as ws_router
app.include_router(ws_router, prefix="/ws")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
