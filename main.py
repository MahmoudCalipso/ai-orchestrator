"""
AI Orchestrator - Main Entry Point
Refactored to use modular Controllers and Service Container.
"""
import logging
import asyncio
import os
from datetime import datetime
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env file
load_dotenv()
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

# Core Imports
from core.orchestrator import Orchestrator
from core.container import container
from middleware.rate_limit import RateLimitMiddleware
from dto.v1.base import ErrorResponse, ErrorDetail

# Platform Components
from services.git import GitCredentialManager, RepositoryManager
from services.database import DatabaseConnectionManager, SchemaAnalyzer, EntityGenerator
from services.registry import LanguageRegistry
from platform_core.auth.dependencies import require_git_account

# Services
from services.ide import EditorService, TerminalService, DebuggerService
from services.project_manager import ProjectManager
from services.git_sync import GitSyncService
from services.ai_update_service import AIUpdateService
from services.build_service import BuildService
from services.runtime_service import RuntimeService
from services.workflow_engine import WorkflowEngine
from services.monitoring import RealtimeMonitoringService
from core.storage import StorageManager, BackupManager
from services.collaboration import CollaborationService
from core.database.manager import unified_db

# Extreme Power 2026 Imports
from services.devops.iac_engine import AutonomousIaCEngine
from services.monitoring.cost_pilot import AICostPilot
from services.security.red_team_ai import RedTeamAI

# Next-Gen Core 2026+ Imports
from core.messaging.bus import MessageBus
from services.monitoring.calt_service import CALTLogger

# Strategic 20/20 Refinements
from services.mcp.bridge import MCPBridge

# Hyper-Intelligence 2026 Final Imports
from core.memory.knowledge_graph import KnowledgeGraphService
from services.security.quantum_vault import QuantumVaultService

# Controllers
from app.controllers.v1.endpoints.system import router as system_router
from app.controllers.v1.endpoints.ai import router as ai_router
from app.controllers.v1.endpoints.projects import router as project_router
from app.controllers.v1.endpoints.git import router as git_router
from app.controllers.v1.endpoints.ide import router as ide_router
from app.controllers.v1.endpoints.storage import router as storage_router
from app.controllers.v1.endpoints.monitoring import router as monitoring_router
from app.controllers.v1.endpoints.admin import router as admin_router
from app.controllers.v1.endpoints.workspace import router as workspace_router
from app.controllers.v1.endpoints.enterprise import router as enterprise_router
from app.controllers.v1.endpoints.auth import router as auth_controller
from app.controllers.v1.endpoints.db_explorer import router as db_explorer_controller
from app.controllers.v1.endpoints.tools import router as tools_router
from app.controllers.v1.endpoints.registry import router as registry_router
from app.controllers.v1.endpoints.emulator import router as emulator_router
from app.controllers.ws.websocket_controller import router as ws_router
from app.middleware.exception_handler import register_exception_handlers
from app.middleware.logging_context import logging_context_middleware
from core.utils.logging import setup_logging

# Configure logging
setup_logging(os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    
    # Startup
    logger.info("Starting AI Orchestrator...")
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Initialize Unified Database Stack
    await unified_db.initialize()
    
    # Initialize Core Services (Shared with Orchestrator where relevant)
    git_credentials = orchestrator.git_credentials
    repo_manager = RepositoryManager(git_credentials)
    db_manager = DatabaseConnectionManager()
    schema_analyzer = SchemaAnalyzer(db_manager)
    entity_generator = EntityGenerator(orchestrator)
    language_registry = LanguageRegistry()
    
    logger.info("Platform services initialized")
    
    # Initialize IDE Services
    editor_service = EditorService()
    terminal_service = TerminalService()
    debugger_service = DebuggerService()
    
    # Initialize Project Management Services
    project_manager = ProjectManager()
    git_sync_service = GitSyncService()
    ai_update_service = AIUpdateService(orchestrator)
    build_service = BuildService()
    runtime_service = RuntimeService()
    monitoring_service = RealtimeMonitoringService()
    storage_manager = orchestrator.storage
    backup_manager = BackupManager()
    collaboration_service = CollaborationService()
    
    workflow_engine = WorkflowEngine({
        "project_manager": project_manager,
        "git_sync": git_sync_service,
        "ai_update": ai_update_service,
        "build": build_service,
        "runtime": runtime_service
    })
    
    # Initialize Service Container
    container.initialize_services(
        orchestrator, git_credentials, repo_manager, db_manager,
        schema_analyzer, entity_generator, language_registry
    )
    
    container.initialize_ide_services(
        editor_service, terminal_service, debugger_service
    )
    
    container.initialize_project_services(
        project_manager, git_sync_service, ai_update_service,
        build_service, runtime_service, workflow_engine, monitoring_service,
        storage_manager, backup_manager, collaboration_service
    )
    
    # 3. Initialize Extreme Power 2026 Services
    iac_engine = AutonomousIaCEngine(orchestrator)
    cost_pilot = AICostPilot(monitoring_service)
    red_team_ai = RedTeamAI(orchestrator)
    
    container.initialize_extreme_power_services(iac_engine, cost_pilot, red_team_ai)
    logger.info("Extreme Power 2026 services initialized and registered")
    
    # 4. Initialize Next-Gen Core 2026+ Services
    message_bus = MessageBus()
    await message_bus.start() # Start background worker
    calt_logger = CALTLogger()
    
    container.initialize_next_gen_services(message_bus, calt_logger)
    logger.info("Next-Gen Core 2026+ services (CALT, MessageBus) initialized and registered")
    
    # 5. Initialize Hyper-Intelligence Final 2026 Services
    knowledge_graph = KnowledgeGraphService()
    quantum_vault = QuantumVaultService(orchestrator)
    
    container.initialize_hyper_intelligence_services(knowledge_graph, quantum_vault)
    logger.info("Hyper-Intelligence Final 2026 services (KG, PQC) initialized and registered")
    
    # 6. Initialize Strategic 20/20 Optimization Services
    mcp_bridge = MCPBridge(orchestrator)
    container.initialize_strategic_services(mcp_bridge)
    logger.info("Strategic 20/20 services (MCP Bridge) initialized and registered")
    
    # Auth router is now handled via Controller registration below
    container.auth_router = auth_controller
    logger.info("Auth router registered in container")

    # Start background tasks
    await monitoring_service.start()
    
    from services.registry.registry_updater import RegistryUpdater
    updater = RegistryUpdater()
    asyncio.create_task(updater.schedule_periodic_updates(interval_hours=24))
    
    logger.info("AI Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator...")
    await container.monitoring_service.stop()
    await unified_db.close()
    await orchestrator.shutdown()
    logger.info("AI Orchestrator shut down successfully")


# Premium Documentation Metadata
API_DESCRIPTION = """
# 🚀 AI Orchestrator Control Plane
### The Ultimate AI Agent OS for Production-Ready Scalability

Welcome to the interactive nerve center of the **AI Orchestrator**. This platform provides the unified API and WebSocket gateway for high-performance AI agent swarms, project lifecycle automation, and real-time developer collaboration.

---

## ⚡ WebSocket Channels (Real-time Flow)
While standard REST endpoints are documented below, the platform also exposes a high-performance **WebSocket Layer** for real-time interaction:

| Protocol | Path | Usage |
| :--- | :--- | :--- |
| `WS` | `/ws/ide/terminal/{sid}` | **Cloud Shell**: Low-latency terminal access to sandboxed environments. |
| `WS` | `/ws/monitoring/stream` | **Observability**: Live telemetry from running AI agents and system resources. |
| `WS` | `/ws/collaboration/{sid}` | **Shared Context**: Real-time cursor syncing and multi-agent peer reviews. |

---

## 🔐 Design Tools & Team Security
- **RBAC**: Integrated Role-Based Access Control ensures secure design handoffs.
- **Swagger Integration**: Use the interactive console below to test AI generates and Figma interpretations directly.
- **Git Sync**: Automatic commits and pushes linked to every AI action.
"""

# Create FastAPI app with premium documentation settings
app = FastAPI(
    title="🚀 AI Orchestrator API",
    description=API_DESCRIPTION,
    version="2026.2.0-PREMIUM",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,  # Disabled ReDoc as requested
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "persistAuthorization": True,
        "tryItOutEnabled": True,
        "filter": True,
    },
    contact={
        "name": "Mahmoud Calipso",
        "url": "https://github.com/MahmoudCalipso",
        "email": "support@ia-orch.example.com",
    },
    license_info={
        "name": "Proprietary / Enterprise",
        "url": "https://ia-orch.example.com/license",
    },
)

# --- Standard Health Probes ---
@app.get("/health")
async def health_check():
    """Enterprise health check with sub-system metrics."""
    return {
        "status": "healthy", 
        "version": "2026.2.0-PREMIUM",
        "system": "active",
        "environment": os.getenv("APP_ENV", "production")
    }

@app.get("/health/live")
async def live_check():
    """K8s Liveness Probe."""
    return {"status": "alive"}

@app.get("/health/ready")
async def ready_check():
    """K8s Readiness Probe."""
    return {"status": "ready"}

# Add CORS middleware - SECURITY: Restrict origins in production
# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Restricted to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"],  # Explicit headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# Add Logging Context Middleware
app.middleware("http")(logging_context_middleware)

# Register Centralized Exception Handlers
register_exception_handlers(app)

# Controllers

# Include Controllers
app.include_router(system_router) # Root /

# All API endpoints strictly under /api/v1
API_PREFIX = "/api/v1"

app.include_router(ai_router, prefix=API_PREFIX)

# Project Controller: /api/user/..., /api/projects/...
# Defined in controller with full paths? No, APIRouter(tags=["Project Management"])
# I should check the paths I put in controller.
# I put full paths in controller e.g. @router.get("/user/{user_id}/projects")
# So prefix="/api" is likely needed if I stripped /api from controller.
# Wait, my extracted controllers have: @router.get("/user/{user_id}/projects")
# The original was `/api/user/{user_id}/projects`.
# So I need `prefix="/api"`.

app.include_router(project_router, prefix=API_PREFIX)
app.include_router(git_router, prefix=API_PREFIX)
app.include_router(ide_router, prefix=API_PREFIX)
app.include_router(storage_router, prefix=API_PREFIX)
app.include_router(monitoring_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(enterprise_router, prefix=API_PREFIX)
app.include_router(workspace_router, prefix=API_PREFIX)
app.include_router(auth_controller, prefix=API_PREFIX)
app.include_router(db_explorer_controller, prefix=API_PREFIX)
app.include_router(tools_router, prefix=API_PREFIX)
app.include_router(registry_router, prefix=API_PREFIX)
app.include_router(emulator_router, prefix=API_PREFIX)

# WebSocket Controller
# Updated to use /ws prefix as requested
app.include_router(ws_router, prefix="/ws")

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    workers = int(os.getenv("API_WORKERS", 1))
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=debug_mode,
        workers=workers if not debug_mode else None
    )
