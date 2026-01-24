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
import uvicorn
from starlette.exceptions import HTTPException as StarletteHTTPException

# Core Imports
from core.orchestrator import Orchestrator
from core.container import container
from middleware.rate_limit import RateLimitMiddleware
from dto.errors.error_response import ErrorResponse, ErrorDetail

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
from controllers.API.system_controller import router as system_router
from controllers.API.ai_controller import router as ai_router
from controllers.API.project_controller import router as project_router
from controllers.API.git_controller import router as git_router
from controllers.API.ide_controller import router as ide_router
from controllers.API.storage_controller import router as storage_router
from controllers.API.monitoring_controller import router as monitoring_router
from controllers.API.admin_controller import router as admin_router
from controllers.API.workspace_controller import router as workspace_router
from controllers.API.enterprise_controller import router as enterprise_router
from controllers.API.auth_controller import router as auth_controller
from controllers.API.db_explorer_controller import router as db_explorer_controller
from controllers.API.tools_controller import router as tools_router
from controllers.API.registry_controller import router as registry_router
from controllers.API.emulator_controller import router as emulator_router
from controllers.WS.websocket_controller import router as ws_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

# Add CORS middleware - SECURITY: Restrict origins in production
# Get allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
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

# --- Global Exception Handler (Magic JSON Errors) ---
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            details={"path": request.url.path}
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        ErrorDetail(field=".".join(map(str, err["loc"])), message=err["msg"], code=err["type"])
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            status="error",
            code="VALIDATION_ERROR",
            message="Input validation failed",
            errors=errors,
            details={"path": request.url.path}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred",
            details={
                "error_type": exc.__class__.__name__,
                "debug": str(exc) if os.getenv("DEBUG") == "true" else "Hidden in production"
            }
        ).model_dump()
    )

# Include Controllers
app.include_router(system_router) # Root /
app.include_router(ai_router, prefix="") # /models, /inference (kept root-level for compat or add /api prefix?) 
# Original main.py had /models at root. /inference at root.
# Let's keep strict compatibility for now, matching main.py paths.
# AI Controller: /models, /inference. So prefix=""

# Project Controller: /api/user/..., /api/projects/...
# Defined in controller with full paths? No, APIRouter(tags=["Project Management"])
# I should check the paths I put in controller.
# I put full paths in controller e.g. @router.get("/user/{user_id}/projects")
# So prefix="/api" is likely needed if I stripped /api from controller.
# Wait, my extracted controllers have: @router.get("/user/{user_id}/projects")
# The original was `/api/user/{user_id}/projects`.
# So I need `prefix="/api"`.

app.include_router(project_router, prefix="/api")

# Git Controller
# Original: /git/config, /git/repositories/...
# Controller: /git/config...
# So prefix=""
app.include_router(git_router)

# IDE Controller
# Original: /api/ide/...
# Controller: /ide/...
# So prefix="/api"
app.include_router(ide_router, prefix="/api")

# Storage Controller
# Original: /api/storage/...
# Controller: /storage/...
# So prefix="/api"
app.include_router(storage_router, prefix="/api")

# Monitoring Controller
# Original: /api/monitoring/...
# Controller: /monitoring/...
# So prefix="/api"
app.include_router(monitoring_router, prefix="/api")

# Admin Controller
# Original: /api/admin/...
# Controller: /admin/...
# So prefix="/api"
app.include_router(admin_router, prefix="/api")

# Enterprise Controller (New)
app.include_router(enterprise_router, prefix="/api")

app.include_router(workspace_router, prefix="/api")

# Auth Controller
app.include_router(auth_controller, prefix="/api")

# DB Explorer Controller
app.include_router(db_explorer_controller, prefix="/api")

# Tools Controller
# Original: /api/figma..., /api/kubernetes...
# Controller: /api/figma... (Wait, I checked tools_controller.py, I put /api/figma/analyze)
# So prefix="" for tools controller.
app.include_router(tools_router)

# Registry Controller
app.include_router(registry_router, prefix="/api")

# Emulator Controller
app.include_router(emulator_router, prefix="/api")

# WebSocket Controller
# Original: /api/ide/terminal..., /api/monitoring/stream...
# Controller: /ide/terminal..., /monitoring/stream
# Updated to use /ws prefix as requested
app.include_router(ws_router, prefix="/ws")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
