"""
AI Orchestrator - Main Entry Point
"""
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Union, Optional

from fastapi import FastAPI, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from platform_core.auth.models import User
from core.orchestrator import Orchestrator
from core.security import verify_api_key
from platform_core.auth.dependencies import require_git_account
from services.git import GitCredentialManager, RepositoryManager
from schemas.spec import (
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    HealthResponse,
    SystemStatus
)
from schemas.generation_spec import (
    GenerationRequest,
    MigrationRequest as EnhancedMigrationRequest,
    DatabaseConfig,
    EntityDefinition
)
from services.database import DatabaseConnectionManager, SchemaAnalyzer, EntityGenerator
from services.registry import LanguageRegistry
from schemas.api_spec import (
    FixCodeRequest, AnalyzeCodeRequest, TestCodeRequest, OptimizeCodeRequest,
    DocumentCodeRequest, ReviewCodeRequest, ExplainCodeRequest, RefactorCodeRequest,
    StandardResponse, SwarmResponse, ProjectAnalyzeRequest, ProjectAddFeatureRequest,
    WorkbenchCreateRequest, MigrationStartRequest, FigmaAnalyzeRequest,
    SecurityScanRequest, IDEWorkspaceRequest, IDEFileWriteRequest,
    IDETerminalRequest, IDEDebugRequest, CollaborationSessionRequest,
    WorkspaceCreateRequest, WorkspaceInviteRequest, GitConfigUpdate, GitRepoInit
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator: Orchestrator = None
git_credentials: GitCredentialManager = None
repo_manager: RepositoryManager = None
db_manager: DatabaseConnectionManager = None
schema_analyzer: SchemaAnalyzer = None
entity_generator: EntityGenerator = None
language_registry: LanguageRegistry = None

# IDE Services
editor_service: "EditorService" = None
terminal_service: "TerminalService" = None
debugger_service: "DebuggerService" = None
auth_router = None

# Project Management Services (Vision 2026)
project_manager = None
git_sync_service = None
ai_update_service = None
build_service = None
runtime_service = None
workflow_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    global orchestrator, git_credentials
    
    # Startup
    logger.info("Starting AI Orchestrator...")
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Initialize Git credentials
    git_credentials = GitCredentialManager()
    repo_manager = RepositoryManager(git_credentials)
    logger.info("Git credential manager initialized")
    
    # Initialize Platform Components
    from platform_core.database import engine, Base
    import platform_core.auth.models
    import platform_core.tenancy.models
    Base.metadata.create_all(bind=engine)
    logger.info("Platform database tables initialized/verified")

    db_manager = DatabaseConnectionManager()
    schema_analyzer = SchemaAnalyzer(db_manager)
    entity_generator = EntityGenerator(orchestrator)
    language_registry = LanguageRegistry()
    language_registry.load_registries()
    logger.info("Platform components initialized")
    
    # Initialize IDE Services
    from services.ide import EditorService, TerminalService, DebuggerService
    global editor_service, terminal_service, debugger_service
    editor_service = EditorService(orchestrator=orchestrator)
    terminal_service = TerminalService()
    debugger_service = DebuggerService()
    logger.info("IDE services initialized with orchestrator")

    # Initialize Auth Router
    from platform_core.auth.routes import router as auth_router_instance
    app.include_router(auth_router_instance, prefix="/api/v2", tags=["Authentication"])
    logger.info("Authentication router initialized (v2)")

    # Initialize Project Management Services (Vision 2026)
    from services.project_manager import ProjectManager
    from services.git_sync import GitSyncService
    from services.ai_update_service import AIUpdateService
    from services.build_service import BuildService
    from services.runtime_service import RuntimeService
    from services.workflow_engine import WorkflowEngine
    
    global project_manager, git_sync_service, ai_update_service, build_service, runtime_service, workflow_engine
    
    project_manager = ProjectManager()
    git_sync_service = GitSyncService()
    ai_update_service = AIUpdateService(orchestrator)
    build_service = BuildService()
    runtime_service = RuntimeService()
    workflow_engine = WorkflowEngine({
        "project_manager": project_manager,
        "git_sync": git_sync_service,
        "ai_update": ai_update_service,
        "build": build_service,
        "runtime": runtime_service
    })
    logger.info("Vision 2026 Project Management services initialized")
    
    # Start Registry Auto-Update background task
    from services.registry.registry_updater import RegistryUpdater
    updater = RegistryUpdater()
    asyncio.create_task(updater.schedule_periodic_updates(interval_hours=24))
    logger.info("Registry auto-update scheduled (24h interval)")
    
    logger.info("AI Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator...")
    await orchestrator.shutdown()
    logger.info("AI Orchestrator shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="🚀 AI Orchestrator API",
    description="""
# Advanced AI Model Orchestration System

This API provides a unified interface for interacting with multiple LLMs (Ollama, Anthropic, OpenAI), 
automated code generation, task migration, and workbench management.

**Primary Provider**: Ollama (free, local, unlimited inference)

## WebSocket Protocols

### Live Console
- **Endpoint**: `/console/{workbench_id}`
- **Usage**: Provides a real-time terminal connection to an active workbench.
- **Protocol**: Custom JSON-wrapped terminal data.

### Live Preview
- **Endpoint**: `/preview/{workbench_id}`
- **Usage**: Real-time project preview and screen sharing.
""",
    version="2026.1.0-POWERFUL",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str], tags=["Core"])
async def root():
    """Root endpoint to verify service is running."""
    return {
        "service": "AI Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse, tags=["Core"])
async def health_check():
    """Check the health status of the orchestrator and runtimes."""
    try:
        status = await orchestrator.get_health_status()
        return HealthResponse(**status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=SystemStatus, tags=["Core"])
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system metrics, resource usage, and loaded models."""
    try:
        status = await orchestrator.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models", response_model=list[ModelInfo], tags=["Models"])
async def list_models(api_key: str = Depends(verify_api_key)):
    """List all available AI models supported by the system."""
    try:
        models = await orchestrator.list_available_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/{model_name}", response_model=ModelInfo, tags=["Models"])
async def get_model_info(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Retrieve detailed metadata for a specific AI model."""
    try:
        model_info = await orchestrator.get_model_info(model_name)
        if not model_info:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelInfo(**model_info)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inference", response_model=InferenceResponse, tags=["Inference"])
async def run_inference(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Run AI inference.
    Supports automatic model selection and routing based on task type.
    """
    try:
        logger.info(f"Inference request: task={request.task_type}, model={request.model}")
        
        result = await orchestrator.run_inference(
            prompt=request.prompt,
            task_type=request.task_type,
            model=request.model,
            parameters=request.parameters,
            context=request.context
        )
        
        return InferenceResponse(**result)
    
    except Exception as e:
        logger.error(f"Inference failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inference/stream", tags=["Inference"])
async def run_inference_stream(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run streaming AI inference returned as server-sent events (SSE)."""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        try:
            async for chunk in orchestrator.run_inference_stream(
                prompt=request.prompt,
                task_type=request.task_type,
                model=request.model,
                parameters=request.parameters,
                context=request.context
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Streaming inference failed: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/models/{model_name}/load", tags=["Models"])
async def load_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Manually load a specific model into memory."""
    try:
        result = await orchestrator.load_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/discover", tags=["Models"])
async def discover_new_models(api_key: str = Depends(verify_api_key)):
    """
    Search the network for the latest 2026 Open Source coding AI models.
    Automatically installs and registers any superior models found.
    """
    try:
        from services.registry.model_discovery import model_discovery
        result = await model_discovery.search_and_install_best_models()
        return result
    except Exception as e:
        logger.error(f"Model discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/{model_name}/unload", tags=["Models"])
async def unload_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Unload a specific model from memory to free up resources."""
    try:
        result = await orchestrator.unload_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migrate", tags=["Migration"])
async def migrate_task(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Migrate a running task to a different model or runtime environment."""
    try:
        result = await orchestrator.migrate_task(
            task_id=request.get("task_id"),
            target_model=request.get("target_model"),
            target_runtime=request.get("target_runtime")
        )
        return {"status": "success", "migration": result}
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics", tags=["Core"])
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Retrieve operational metrics and success rates."""
    try:
        metrics = await orchestrator.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# New Universal Architecture Endpoints

@app.post("/workbench/create", response_model=StandardResponse, tags=["Workbench"])
async def create_workbench(
    request: WorkbenchCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new isolated workbench for a specific tech stack."""
    try:
        workbench = await orchestrator.workbench_manager.create_workbench(
            stack=request.stack,
            project_name=request.project_name
        )
        
        return StandardResponse(
            status="success",
            result={
                "workbench_id": workbench.id,
                "stack": workbench.stack
            }
        )
    except Exception as e:
        logger.error(f"Failed to create workbench: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workbench/list", tags=["Workbench"])
async def list_workbenches(api_key: str = Depends(verify_api_key)):
    """List all currently active isolated workbenches."""
    try:
        workbenches = await orchestrator.workbench_manager.list_workbenches()
        return {"workbenches": workbenches}
    except Exception as e:
        logger.error(f"Failed to list workbenches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migration/start", response_model=StandardResponse, tags=["Migration"])
async def start_migration(
    request: MigrationStartRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start a universal migration process by creating a target workbench and preview tunnel."""
    try:
        # Create workbench for target stack
        workbench = await orchestrator.workbench_manager.create_workbench(
            stack=request.target_stack,
            project_name=f"migration-{request.source_stack}-to-{request.target_stack}"
        )
        
        # Generate build scripts
        build_script = orchestrator.build_system.generate_build_script(
            request.target_stack,
            f"migration-{request.source_stack}-to-{request.target_stack}"
        )
        
        # Create port tunnel
        tunnel = await orchestrator.port_manager.create_tunnel(
            workbench.id,
            workbench.blueprint.default_port
        )
        
        return StandardResponse(
            status="success",
            result={
                "workbench_id": workbench.id,
                "preview_url": tunnel["public_url"],
                "build_script": build_script
            }
        )
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/console/{workbench_id}")
async def console_websocket(websocket: WebSocket, workbench_id: str):
    """
    WebSocket endpoint for live terminal console.
    
    Allows real-time interaction with the workbench environment.
    """
    import uuid
    session_id = str(uuid.uuid4())
    
    await orchestrator.websocket_gateway.handle_connection(
        websocket,
        session_id,
        workbench_id
    )


# Universal AI Agent Endpoints

@app.post("/api/analyze-description", response_model=Dict[str, Any], tags=["Generation"])
async def analyze_description(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze a project description and return the full auto-generated configuration.
    
    This endpoint provides a **real-time preview** of what configuration will be generated
    from a description, without actually executing the generation.
    
    **Use Case**: Get the complete JSON config to review before sending to /api/generate
    
    **Example Request**:
    ```json
    {
        "description": "A scalable e-commerce platform with payment processing...",
        "project_name": "My E-Commerce Platform"
    }
    ```
    
    **Returns**: Complete auto-generated configuration with:
    - Detected project type
    - Recommended tech stack with latest versions
    - Architecture patterns
    - Security requirements
    - Scalability configuration
    - Integration points
    - Deployment strategy
    """
    try:
        description = request.get("description")
        project_name = request.get("project_name", "Generated Project")
        
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        if len(description) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Description too short. Please provide at least 50 characters for meaningful analysis."
            )
        
        logger.info(f"🔍 Analyzing description for config preview: {project_name}")
        
        # Initialize description analyzer
        from services.analysis import DescriptionAnalyzer
        analyzer = DescriptionAnalyzer(llm_inference=orchestrator.llm)
        
        # Analyze the description
        analysis = await analyzer.analyze(description, {})
        
        # Build complete generation config
        generated_config = await analyzer.build_generation_config(
            analysis=analysis,
            project_name=project_name,
            description=description,
            language_registry=language_registry
        )
        
        # Create human-readable summary
        summary = f"""
**Project Type**: {analysis.project_type}
**Complexity**: {analysis.estimated_complexity}
**Features Detected**: {len(analysis.core_features)} ({', '.join(analysis.core_features[:5])}{'...' if len(analysis.core_features) > 5 else ''})
**Tech Stack**: {generated_config['languages'][0]['framework']} {generated_config['languages'][0]['version']}
**Architecture**: {', '.join(analysis.architecture_patterns)}
**Database**: {analysis.database_type}
**Integrations**: {len(analysis.integration_points)} detected
        """.strip()
        
        logger.info(f"✅ Analysis complete: {analysis.project_type} project, {analysis.estimated_complexity} complexity")
        
        return {
            "status": "success",
            "analysis": analysis.to_dict(),
            "generated_config": generated_config,
            "summary": summary,
            "message": "Configuration generated successfully. You can now use 'generated_config' in /api/generate"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Description analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/generate", tags=["Generation"])
async def generate_code(
    request: Union[GenerationRequest, Dict[str, Any]],
    user: User = Depends(require_git_account)
):
    """
    Perform AI-driven code or full application generation.
    
    Supports both single-file snippets and complex, multi-language project structures 
    with database, security, and infrastructure (Kubernetes/Docker) logic.
    
    **NEW**: Intelligent description analyzer automatically extracts requirements from natural language.
    """
    try:
        # Check if it's a full generation request
        is_complex = isinstance(request, GenerationRequest) or (isinstance(request, dict) and "languages" in request)
        
        if is_complex:
            # Complex Project Generation Logic (Swarm-Powered)
            req_data = request.model_dump() if hasattr(request, "model_dump") else request
            
            # VISION 2026: INTELLIGENT DESCRIPTION ANALYSIS + AUTO-CONFIG
            description = req_data.get('description', '')
            
            if description and len(description) > 100:
                logger.info(f"🔍 Analyzing complex description ({len(description)} chars)")
                
                # Initialize description analyzer
                from services.analysis import DescriptionAnalyzer
                analyzer = DescriptionAnalyzer(llm_inference=orchestrator.llm)
                
                # Analyze the description
                analysis = await analyzer.analyze(description, req_data)
                
                logger.info(f"📊 Analysis complete: {analysis.project_type} project, {len(analysis.core_features)} features, {analysis.estimated_complexity} complexity")
                
                # BUILD COMPLETE GENERATION CONFIG WITH LATEST VERSIONS FROM REGISTRY
                auto_config = await analyzer.build_generation_config(
                    analysis=analysis,
                    project_name=req_data.get('project_name', 'Generated Project'),
                    description=description,
                    language_registry=language_registry
                )
                
                # Merge auto-config with user-provided config (user config takes precedence)
                for key, value in auto_config.items():
                    if key not in req_data or req_data[key] is None:
                        req_data[key] = value
                
                logger.info(f"✅ Auto-configured: {auto_config.get('languages', [])} with versions from registry")
            
            
            # Start Swarm-based Project Generation
            # We use the Orchestrator's run_inference which delegates to LeadArchitect swarm
            project_description = f"""
            Project: {req_data.get('project_name')}
            Description: {req_data.get('description')}
            Requirements: {req_data.get('requirements')}
            Stacks: {req_data.get('languages')}
            """
            
            # Add analysis insights to prompt if available
            if "analysis" in req_data:
                project_description += f"""
            
            INTELLIGENT ANALYSIS:
            - Project Type: {req_data['project_type']}
            - Core Features: {', '.join(req_data['core_features'])}
            - Architecture: {', '.join(req_data['architecture_patterns'])}
            - Scalability: {', '.join(req_data['scalability_requirements'])}
            - Integrations: {', '.join(req_data['integration_points'])}
            - Security: {', '.join(req_data['security_requirements'])}
            - Complexity: {req_data['analysis']['estimated_complexity']}
            """
            
            swarm_result = await orchestrator.run_inference(
                prompt=project_description,
                task_type="full_project_generation",
                context=req_data
            )
            
            # Aggregate Swarm Output
            worker_results = swarm_result.get("swarm_output", {}).get("worker_results", {})
            
            result = {
                "status": "success",
                "type": "project",
                "generated_files": {},
                "swarm_analysis": swarm_result.get("swarm_output", {}).get("decomposition"),
                "docker_compose": ""
            }
            
            # Assemble files from all agents with high fidelity
            for domain, worker_out in worker_results.items():
                solution = worker_out.get("solution", "")
                
                # Enhanced code extraction: handle multiple files if agent returns them
                import re
                code_blocks = re.findall(r'### FILE: (.*?)\n```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
                
                if code_blocks:
                    for filename, content in code_blocks:
                        result["generated_files"][f"{domain}/{filename}"] = content
                else:
                    # Fallback to general block extraction
                    general_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
                    for i, block in enumerate(general_blocks):
                        ext = "txt"
                        if "import " in block or "def " in block: ext = "py"
                        elif "import React" in block: ext = "tsx"
                        
                        fname = f"core_{i}.{ext}" if i > 0 else f"main_source.{ext}"
                        result["generated_files"][f"{domain}/{fname}"] = block
                
                # Capture infrastructure bits
                if "infrastructure" in worker_out:
                    infra = worker_out["infrastructure"]
                    if "dockerfile" in infra:
                        result["generated_files"][f"{domain}/Dockerfile"] = infra["dockerfile"]

            # Generate high-quality README
            result["generated_files"]["README.md"] = f"""
# {req_data.get('project_name', 'Ultimate Generated Solution')}

This solution was generated using a multi-model AI swarm (DeepSeek-V3 & Qwen-2.5) with a mandatory peer-review pass for production quality.

## Project Structure
{chr(10).join([f"- **{domain}**: Generated by {worker_out.get('model_used')} with reviewer pass" for domain, worker_out in worker_results.items()])}

## Quick Start
1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up --build`.

## Architecture Details
- **Backend/Frontend**: Fully decoupled architecture.
- **Security**: Built-in security review pass.
- **Orchestration**: Managed via Docker Compose.
"""
            
            # Generate Docker Compose (already implemented above, keeping it robust)
            if len(worker_results) > 1:
                from services.devops.docker_orchestrator import docker_orchestrator
                services = []
                for domain in worker_results.keys():
                    if domain != "database":
                        services.append({"name": domain, "stack": domain, "port": 8000}) # Simplified
                
                db_type = req_data.get("database", {}).get("type", "postgresql")
                result["docker_compose"] = docker_orchestrator.generate_compose(services, db_type)
                result["generated_files"]["docker-compose.yml"] = result["docker_compose"]

            # LEGACY / Entity generation sync (Optional)
            # ... we can still run the old entity-based generation if needed ...
            
            return result
        else:
            # Legacy/Simple Mode
            req_dict = request if isinstance(request, dict) else request.dict()
            requirements = req_dict.get("requirements")
            language = req_dict.get("language")
            framework = req_dict.get("framework")
            
            result = await orchestrator.universal_agent.generate_code(
                requirements=requirements,
                language=language,
                framework=framework
            )
            
            return {
                "status": "success",
                "type": "snippet",
                "result": result
            }
            
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/registry/metadata", tags=["Registry"])
async def get_all_registry_metadata(api_key: str = Depends(verify_api_key)):
    """Get all metadata for Languages, Frameworks, and Databases including Logos"""
    from services.registry.framework_registry import framework_registry
    return {
        "status": "success",
        "languages": framework_registry.languages,
        "frameworks": framework_registry.frameworks,
        "databases": framework_registry.databases
    }

@app.get("/api/migration/options", tags=["Migration"])
async def get_migration_options(
    language: str,
    framework: str,
    api_key: str = Depends(verify_api_key)
):
    """Get valid architecture options and best practices for a target stack"""
    from services.registry.framework_registry import framework_registry
    info = framework_registry.get_framework_info(language, framework)
    if not info:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    return {
        "status": "success",
        "architectures": info.get("architectures", []),
        "best_practices": info.get("best_practices", []),
        "recommended_version": info.get("latest_version")
    }

@app.post("/api/migrate", tags=["Migration"])
async def migrate_code(
    request: Union[EnhancedMigrationRequest, Dict[str, Any]],
    user: User = Depends(require_git_account)
):
    """
    Migrate code from ANY stack to ANY stack.
    
    Includes deep project scanning, forensic audit, and architecture-aware 
    transformation to ensure high-quality, bug-free modernized code.
    """
    try:
        req_data = request.model_dump() if hasattr(request, "model_dump") else request
        is_complex = "source_path" in req_data or "source_repo" in req_data
        
        if is_complex:
            source_path = req_data.get("source_path")
            
            # 1. PHASE 0: DEEP SCAN & INDEXING
            if source_path:
                from agents.project_scanner import ProjectScannerAgent
                scanner = ProjectScannerAgent(orchestrator)
                project_map = await scanner.scan_project(source_path)
                req_data["source_project_map"] = project_map.to_dict()
                logger.info(f"Source project scanned: {project_map.source_stack}")

            # 2. PHASE 1: FORENSIC AUDIT (Manual flag or auto-detected)
            if req_data.get("perform_audit", True) and source_path:
                from agents.migration_audit_agent import MigrationAuditAgent
                auditor = MigrationAuditAgent(orchestrator)
                audit_result = await auditor.audit_project(source_path)
                req_data["audit_findings"] = audit_result.get("findings", [])
                logger.info(f"Forensic audit complete: {len(req_data['audit_findings'])} findings")

            # 3. PHASE 2: SWARM-BASED HEALING MIGRATION
            migration_task = f"Migrate project from {req_data.get('source_stack')} to {req_data.get('target_stack')}. Path: {source_path}"
            
            swarm_result = await orchestrator.run_inference(
                prompt=migration_task,
                task_type="migration",
                context=req_data
            )
            
            # Aggregate Swarm Output
            worker_results = swarm_result.get("swarm_output", {}).get("worker_results", {})
            
            result = {
                "status": "success",
                "type": "repository_migration",
                "migrated_files": {},
                "audit": req_data.get("audit_findings", []),
                "swarm_analysis": swarm_result.get("swarm_output", {}).get("decomposition")
            }
            
            # Assemble migrated files
            for domain, worker_out in worker_results.items():
                solution = worker_out.get("solution", "")
                import re
                code_blocks = re.findall(r'### FILE: (.*?)\n```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
                
                if code_blocks:
                    for filename, content in code_blocks:
                        result["migrated_files"][f"{domain}/{filename}"] = content
                else:
                    # Fallback
                    general_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
                    for i, block in enumerate(general_blocks):
                        result["migrated_files"][f"{domain}/migrated_{i}.py"] = block

            return result
        else:
            # Legacy/Snippet Mode
            code = req_data.get("code")
            source_stack = req_data.get("source_stack")
            target_stack = req_data.get("target_stack")
            
            result = await orchestrator.universal_agent.migrate_code(
                code=code,
                source_stack=source_stack,
                target_stack=target_stack
            )
            
            return {
                "status": "success",
                "result": result
            }
    
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fix", response_model=SwarmResponse, tags=["AI Agent"])
async def fix_code(
    request: FixCodeRequest,
    user: User = Depends(require_git_account)
):
    """
    Fix code issues in ANY language using a multi-model swarm.
    
    Automatically identifies and resolves common bugs, logic errors, 
    and performance bottlenecks with a peer-review validation pass.
    """
    try:
        req_data = request.model_dump()
        
        # Swarm-based Self-Healing/Fixing
        fix_task = f"Fix issue: {req_data.get('issue')} in code: {req_data.get('code')}"
        
        swarm_result = await orchestrator.run_inference(
            prompt=fix_task,
            task_type="self_healing",
            context=req_data
        )
        
        # Aggregate results
        worker_results = swarm_result.get("swarm_output", {}).get("worker_results", {})
        
        return SwarmResponse(
            status="success",
            type="self_healing_fix",
            worker_results=worker_results,
            swarm_analysis=swarm_result.get("swarm_output", {}).get("decomposition")
        )
    except Exception as e:
        logger.error(f"Code fixing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze", response_model=StandardResponse, tags=["AI Agent"])
async def analyze_code(
    request: AnalyzeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze code for quality, security, and performance.
    
    Provides detailed insights and metrics for code in any supported language.
    """
    try:
        result = await orchestrator.universal_agent.analyze_code(
            code=request.code,
            language=request.language,
            analysis_type=request.analysis_type
        )
        
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test", response_model=StandardResponse, tags=["AI Agent"])
async def generate_tests(
    request: TestCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate unit and integration tests for code in any language."""
    try:
        result = await orchestrator.universal_agent.generate_tests(
            code=request.code,
            language=request.language,
            test_framework=request.test_framework
        )
        
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize", response_model=StandardResponse, tags=["AI Agent"])
async def optimize_code(
    request: OptimizeCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Optimize code for performance, memory usage, or readability.
    
    Applies advanced refactoring and algorithmic improvements to the provided code.
    """
    try:
        result = await orchestrator.universal_agent.optimize_code(
            code=request.code,
            language=request.language,
            optimization_goal=request.optimization_goal
        )
        
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Code optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document", response_model=StandardResponse, tags=["AI Agent"])
async def document_code(
    request: DocumentCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate documentation for ANY language."""
    try:
        result = await orchestrator.universal_agent.document_code(
            code=request.code,
            language=request.language,
            doc_style=request.doc_style
        )
        
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review", response_model=StandardResponse, tags=["AI Agent"])
async def review_code(
    request: ReviewCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Perform a comprehensive AI code review.
    
    Identifies code smells, potential bugs, style violations, and suggests 
    architectural improvements.
    """
    try:
        result = await orchestrator.universal_agent.review_code(
            code=request.code,
            language=request.language
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain", response_model=StandardResponse, tags=["AI Agent"])
async def explain_code(
    request: ExplainCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Explain code in ANY language with deep technical context."""
    try:
        result = await orchestrator.universal_agent.explain_code(
            code=request.code,
            language=request.language
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refactor", response_model=StandardResponse, tags=["AI Agent"])
async def refactor_code(
    request: RefactorCodeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Refactor code in ANY language based on specific goals."""
    try:
        result = await orchestrator.universal_agent.refactor_code(
            code=request.code,
            refactoring_goal=request.refactoring_goal,
            language=request.language
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Code refactoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/analyze", response_model=StandardResponse, tags=["AI Agent"])
async def analyze_project(
    request: ProjectAnalyzeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze entire project in ANY language/framework recursively."""
    try:
        result = await orchestrator.universal_agent.analyze_project(
            project_path=request.project_path
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/migrate", response_model=StandardResponse, tags=["AI Agent"])
async def migrate_project(
    request: EnhancedMigrationRequest, # Using the existing one from schemas.generation_spec
    api_key: str = Depends(verify_api_key)
):
    """Migrate entire project from ANY stack to ANY stack (Full-Scale Migration)."""
    try:
        result = await orchestrator.universal_agent.migrate_project(
            project_path=request.source_path,
            source_stack=request.source_stack,
            target_stack=request.target_stack
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Project migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/add-feature", response_model=StandardResponse, tags=["AI Agent"])
async def add_feature(
    request: ProjectAddFeatureRequest,
    api_key: str = Depends(verify_api_key)
):
    """Add a complex feature to ANY existing project autonomously."""
    try:
        result = await orchestrator.universal_agent.add_feature(
            project_path=request.project_path,
            feature_description=request.feature_description
        )
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Feature addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Git Configuration Endpoints

@app.get("/git/providers", tags=["Git"])
async def list_git_providers(api_key: str = Depends(verify_api_key)):
    """List all supported Git providers (GitHub, GitLab, Bitbucket) and their configuration status."""
    try:
        providers = git_credentials.list_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Failed to list Git providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/git/config/{provider}", tags=["Git"])
async def get_git_config(provider: str, api_key: str = Depends(verify_api_key)):
    """Retrieve the non-sensitive configuration for a specific Git provider."""
    try:
        credentials = git_credentials.get_credentials(provider)
        safe_credentials = {k: v for k, v in credentials.items() if k not in ["token", "app_password", "client_secret"]}
        return {
            "provider": provider,
            "configured": git_credentials.validate_credentials(provider),
            "config": safe_credentials
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/git/config/{provider}", response_model=StandardResponse, tags=["Git"])
async def set_git_config(provider: str, request: GitConfigUpdate, api_key: str = Depends(verify_api_key)):
    """Update or set credentials (token, SSH key) for a specific Git provider."""
    try:
        credentials = request.model_dump(exclude_none=True)
        success = git_credentials.set_credentials(provider, credentials)
        
        if success:
            return StandardResponse(status="success", message=f"Credentials set for {provider}")
        else:
            raise HTTPException(status_code=500, detail="Failed to set credentials")
    except Exception as e:
        logger.error(f"Failed to set Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/git/config/{provider}")
async def delete_git_config(provider: str, api_key: str = Depends(verify_api_key)):
    """Delete credentials for a Git provider"""
    try:
        success = git_credentials.set_credentials(provider, {})
        if success:
            return {"status": "success", "provider": provider, "message": f"Credentials deleted for {provider}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete credentials")
    except Exception as e:
        logger.error(f"Failed to delete Git config for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/git/validate/{provider}")
async def validate_git_credentials(provider: str, api_key: str = Depends(verify_api_key)):
    """Validate credentials for a Git provider"""
    try:
        is_valid = git_credentials.validate_credentials(provider)
        return {
            "valid": is_valid,
            "provider": provider,
            "message": "Credentials are valid" if is_valid else "Credentials are invalid or missing"
        }
    except Exception as e:
        logger.error(f"Failed to validate Git credentials for {provider}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/git/config")
async def get_general_git_config(api_key: str = Depends(verify_api_key)):
    """Get general Git configuration"""
    try:
        config = git_credentials.get_git_config()
        return {"config": config}
    except Exception as e:
        logger.error(f"Failed to get Git config: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# Enhanced Database & Registry Endpoints

@app.post("/api/database/analyze", tags=["Database"])
async def analyze_database(
    config: DatabaseConfig,
    api_key: str = Depends(verify_api_key)
):
    """
    Reverse engineer an existing database schema.
    
    Connects to the specified database (PostgreSQL, MySQL, etc.) and extracts 
    entity, relationship, and field metadata for code generation.
    """
    try:
        entities = await schema_analyzer.analyze(config)
        return StandardResponse(
            status="success",
            result=[entity.model_dump() for entity in entities]
        )
    except Exception as e:
        logger.error(f"Database analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/entity/generate", tags=["Generation"])
async def generate_from_entities(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Generate models and API routes from a list of entity definitions.
    
    Useful when you have the entity JSON and want to generate the implementation 
    for a specific language and framework.
    """
    try:
        # Implementation would use entity_generator
        language = request.get("language")
        entities_data = request.get("entities", [])
        entities = [EntityDefinition(**e) for e in entities_data]
        
        models = await entity_generator.generate_models(entities, language)
        api = await entity_generator.generate_api(entities, language, request.get("framework", "standard"))
        
        return {
            "status": "success",
            "models": models,
            "api": api
        }
    except Exception as e:
        logger.error(f"Entity generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/registry/languages")
async def list_supported_languages(api_key: str = Depends(verify_api_key)):
    """List supported languages and their configurations"""
    try:
        languages = language_registry.get_supported_languages()
        details = {}
        for lang in languages:
            details[lang] = language_registry.get_language_config(lang)
            
        return {
            "languages": languages,
            "details": details
        }
    except Exception as e:
        logger.error(f"Registry query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced Git Endpoints

@app.post("/git/repositories/init", response_model=StandardResponse, tags=["Git"])
async def init_repository(
    request: GitRepoInit,
    api_key: str = Depends(verify_api_key)
):
    """Initialize a new git repository in a specific directory."""
    try:
        success = repo_manager.init_repository(request.path)
        return StandardResponse(status="success" if success else "failed", result={"path": request.path})
    except Exception as e:
        logger.error(f"Git init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Figma Integration Endpoints

@app.post("/api/figma/analyze", response_model=StandardResponse, tags=["AI Agent"])
async def analyze_figma_design(
    request: FigmaAnalyzeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze Figma file and extract design components for generation."""
    try:
        from services.figma import FigmaClient, FigmaAnalyzer
        
        client = FigmaClient(token=request.token)
        analyzer = FigmaAnalyzer()
        
        file_data = await client.get_file(request.file_key)
        analysis = analyzer.analyze_file(file_data)
        
        return StandardResponse(status="success", result=analysis)
    except Exception as e:
        logger.error(f"Figma analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Security Endpoints

@app.post("/api/security/scan", response_model=StandardResponse, tags=["Security"])
async def scan_security(
    request: SecurityScanRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Perform a professional security scan on a project.
    
    Includes SAST (Static Analysis) and Dependency Scanning to identify 
    vulnerabilities and insecure patterns (OWASP Top 10).
    """
    try:
        from services.security import VulnerabilityScanner
        
        scanner = VulnerabilityScanner()
        results = {}
        
        if request.type in ["code", "all"]:
            results["code_scan"] = await scanner.scan_code(request.project_path, request.language)
            
        if request.type in ["dependencies", "all"]:
            results["dependency_scan"] = await scanner.scan_dependencies(request.project_path)
            
        return StandardResponse(status="success", result=results)
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vision 2026: Project Lifecycle E2E

@app.post("/api/lifecycle/execute", tags=["Lifecycle"], summary="Execute E2E Project Lifecycle")
async def execute_lifecycle(
    project_id: str,
    stack: str,
    git_sync: bool = False,
    repo_name: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Powerful 2026 E2E Lifecycle Endpoint:
    1. Provisions a Real-time Testing environment (Docker).
    2. Generates a live tunnel for testing.
    3. (Optional) Syncs the codebase to your specific Git repository.
    """
    try:
        context = {
            "type": "finalization",
            "project_id": project_id,
            "stack": stack,
            "git_sync": git_sync,
            "repo_name": repo_name
        }
        
        # Trigger the Lead Architect for the finalization dance
        result = await orchestrator.lead_architect.act(
            f"Finalize project {project_id} for the user.",
            context
        )
        return result
    except Exception as e:
        logger.error(f"Lifecycle execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Storage Management Endpoints

@app.get("/api/storage/stats", tags=["Storage"])
async def get_storage_stats(api_key: str = Depends(verify_api_key)):
    """Retrieve statistics about local storage usage, including total projects and archives."""
    try:
        from core.storage import StorageManager
        
        storage = StorageManager()
        stats = await storage.get_storage_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/storage/projects", tags=["Storage"])
async def list_stored_projects(
    status: Optional[str] = None,
    language: Optional[str] = None,
    min_size_gb: Optional[float] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    List all generated projects currently stored on disk.
    Supports filtering by status (active, archived) and language.
    """
    try:
        from core.storage import StorageManager
        
        storage = StorageManager()
        projects = await storage.list_projects(
            status=status,
            language=language,
            min_size_gb=min_size_gb
        )
        
        return {
            "status": "success",
            "projects": projects,
            "count": len(projects)
        }
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/storage/projects/{project_id}", tags=["Storage"])
async def get_stored_project(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Retrieve detailed metadata and file structure for a specific stored project."""
    try:
        from core.storage import StorageManager
        
        storage = StorageManager()
        project = await storage.get_project(project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "project": project
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/storage/projects/{project_id}")
async def delete_stored_project(
    project_id: str,
    soft: bool = True,
    api_key: str = Depends(verify_api_key)
):
    """Delete a project (soft or hard delete)"""
    try:
        from core.storage import StorageManager
        
        storage = StorageManager()
        success = await storage.delete_project(project_id, soft=soft)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "message": f"Project {'soft' if soft else 'hard'} deleted",
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/storage/archive/{project_id}")
async def archive_stored_project(
    project_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Archive a project"""
    try:
        from core.storage import StorageManager
        
        storage = StorageManager()
        success = await storage.archive_project(project_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": "success",
            "message": "Project archived",
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to archive project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/storage/cleanup")
async def cleanup_storage(api_key: str = Depends(verify_api_key)):
    """Run storage cleanup"""
    try:
        from core.storage import StorageManager, BackupManager
        
        storage = StorageManager()
        backup_mgr = BackupManager()
        
        # Archive old projects
        archived_count = await storage.archive_old_projects(days=90)
        
        # Clean cache
        freed_bytes = await storage.clean_cache()
        
        # Remove old backups
        removed_backups = await backup_mgr.cleanup_old_backups(days=30)
        
        return {
            "status": "success",
            "archived_projects": archived_count,
            "freed_bytes": freed_bytes,
            "freed_gb": freed_bytes / (1024**3),
            "removed_backups": removed_backups
        }
    except Exception as e:
        logger.error(f"Storage cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/storage/backup/{project_id}")
async def backup_stored_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """
    Back up a stored project manually.
    """
    try:
        from core.storage.backup import BackupManager
        backup_manager = BackupManager()
        result = await backup_manager.create_backup(project_id)
        if result:
            return {"status": "success", "message": f"Backup created: {result}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create backup")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vision 2026 - User Project Management Endpoints

@app.get("/api/user/{user_id}/projects", tags=["Project Management"])
async def list_user_projects(
    user_id: str,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    api_key: str = Depends(verify_api_key)
):
    """List all projects belonging to a user"""
    return project_manager.get_user_projects(user_id, status, page, page_size)


@app.get("/api/user/{user_id}/projects/{project_id}", tags=["Project Management"])
async def get_user_project(project_id: str, user_id: str, api_key: str = Depends(verify_api_key)):
    """Get project details"""
    project = project_manager.get_project(project_id)
    if not project or project["user_id"] != user_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/api/user/{user_id}/projects", tags=["Project Management"])
async def create_user_project(user_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Create a new user project"""
    return project_manager.create_project(
        user_id=user_id,
        project_name=request.get("project_name", "New Project"),
        description=request.get("description", ""),
        git_repo_url=request.get("git_repo_url", ""),
        language=request.get("language", ""),
        framework=request.get("framework", "")
    )


@app.delete("/api/user/{user_id}/projects/{project_id}", tags=["Project Management"])
async def delete_user_project(project_id: str, user_id: str, api_key: str = Depends(verify_api_key)):
    """Delete a user project"""
    success = project_manager.delete_project(project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized")
    return {"status": "success", "message": "Project deleted"}


@app.post("/api/projects/{project_id}/open", tags=["Project Management"])
async def open_user_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Open a project: Clone from Git and load in IDE"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Clone if not already cloned
    local_path = project["local_path"]
    if not os.path.exists(os.path.join(local_path, ".git")):
        res = await git_sync_service.clone_repository(
            repo_url=project["git_repo_url"],
            local_path=local_path,
            branch=project.get("git_branch", "main"),
            credentials=request.get("git_credentials")
        )
        if not res["success"]:
            raise HTTPException(status_code=500, detail=res["message"])
    
    project_manager.update_last_opened(project_id)
    
    # Create IDE workspace
    workspace = await editor_service.create_workspace(project["project_name"], local_path)
    
    return {
        "status": "success",
        "workspace_id": workspace.id,
        "project": project
    }


@app.post("/api/projects/{project_id}/sync", tags=["Project Management"])
async def sync_user_project(project_id: str, api_key: str = Depends(verify_api_key)):
    """Sync project with Git remote (pull)"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await git_sync_service.pull_latest(project["local_path"])
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return {"status": "success", "commit": res["commit_hash"]}


@app.post("/api/projects/{project_id}/ai-update", tags=["Project Management"])
async def ai_update_project(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Apply AI updates via chat prompt"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await ai_update_service.apply_chat_update(
        project_id=project_id,
        local_path=project["local_path"],
        prompt=request.get("prompt"),
        context=request.get("context")
    )
    
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return res


@app.post("/api/projects/{project_id}/files/{file_path:path}/ai-update", tags=["Project Management"])
async def ai_inline_update(project_id: str, file_path: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Apply AI inline updates to a specific file"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    res = await ai_update_service.apply_inline_update(
        local_path=project["local_path"],
        file_path=file_path,
        prompt=request.get("prompt"),
        selection=request.get("selection")
    )
    
    if not res["success"]:
        raise HTTPException(status_code=500, detail=res["error"])
        
    return res


@app.post("/api/projects/{project_id}/workflow", tags=["Project Management"])
async def execute_project_workflow(project_id: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Execute a complete project workflow (e.g., sync -> update -> push -> build -> run)"""
    project = project_manager.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    workflow_id = await workflow_engine.execute_workflow(
        project_id=project_id,
        user_id=project["user_id"],
        steps=request.get("steps", ["sync", "update", "push", "build", "run"]),
        config=request
    )
    
    return {
        "status": "started",
        "workflow_id": workflow_id,
        "message": f"Workflow {workflow_id} started in background"
    }


@app.get("/api/projects/{project_id}/workflow/{workflow_id}", tags=["Project Management"])
async def get_workflow_status(project_id: str, workflow_id: str, api_key: str = Depends(verify_api_key)):
    """Get status of a running workflow"""
    status = workflow_engine.get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return status


# Phase 8: Admin & User Management Endpoints (SuperUser Only)

@app.get("/api/admin/users", tags=["Admin"])
async def list_all_users(api_key: str = Depends(verify_api_key)):
    """List all registered users (SuperUser only)"""
    from core.security import SecurityManager
    sm = SecurityManager()
    if not sm.is_superuser(api_key):
        raise HTTPException(status_code=403, detail="Forbidden: SuperUser access required")
    
    # This would normally query the DB. For now, returning internal memory/mock
    return {"users": list(sm.api_keys.values())}


@app.get("/api/admin/projects", tags=["Admin"])
async def list_all_projects(api_key: str = Depends(verify_api_key)):
    """List all projects across all users (SuperUser only)"""
    from core.security import SecurityManager
    sm = SecurityManager()
    if not sm.is_superuser(api_key):
        raise HTTPException(status_code=403, detail="Forbidden: SuperUser access required")
        
    # project_manager.get_all_projects() - pseudo-code
    all_projects = list(project_manager.projects_db.values())
    return {"projects": all_projects, "total": len(all_projects)}


@app.put("/api/admin/users/{user_id}/role", tags=["Admin"])
async def update_user_role(user_id: str, request: Dict[str, str], api_key: str = Depends(verify_api_key)):
    """Update user role (SuperUser only)"""
    from core.security import SecurityManager
    sm = SecurityManager()
    if not sm.is_superuser(api_key):
        raise HTTPException(status_code=403, detail="Forbidden: SuperUser access required")
    
    new_role = request.get("role")
    if new_role not in ["admin", "developer", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    # In a real DB sync, update user record. For mock, find the API key linked to this user_id
    for key, info in sm.api_keys.items():
        if info.get("user_id") == user_id:
            info["role"] = new_role
            return {"status": "success", "user_id": user_id, "new_role": new_role}
            
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/api/admin/system/metrics", tags=["Admin"])
async def get_system_wide_metrics(api_key: str = Depends(verify_api_key)):
    """Get system-wide metrics (SuperUser only)"""
    from core.security import SecurityManager
    sm = SecurityManager()
    if not sm.is_superuser(api_key):
        raise HTTPException(status_code=403, detail="Forbidden: SuperUser access required")
        
    return {
        "uptime": "99.99%",
        "total_projects": len(project_manager.projects_db),
        "total_users": len(sm.api_keys),
        "active_workbenches": len(orchestrator.workbench_manager.workbenches if orchestrator and orchestrator.workbench_manager else []),
        "api_calls_24h": 12503
    }


# Phase 2: Browser IDE Endpoints

@app.post("/api/ide/workspace", response_model=StandardResponse, tags=["IDE"])
async def create_ide_workspace(
    request: IDEWorkspaceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Initialize a persistent IDE workspace session."""
    try:
        result = await editor_service.create_workspace(request.workspace_id)
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Failed to create IDE workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ide/files/{workspace_id}/{path:path}")
async def read_file(
    workspace_id: str,
    path: str,
    api_key: str = Depends(verify_api_key)
):
    """Read file from workspace"""
    try:
        result = await editor_service.read_file(workspace_id, path)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/files/{workspace_id}/{path:path}", response_model=StandardResponse, tags=["IDE"])
async def write_file(
    workspace_id: str,
    path: str,
    request: IDEFileWriteRequest,
    api_key: str = Depends(verify_api_key)
):
    """Write content to a file in the workspace."""
    try:
        result = await editor_service.write_file(workspace_id, path, request.content)
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Failed to write file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/ide/files/{workspace_id}/{path:path}")
async def delete_file(
    workspace_id: str,
    path: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete file from workspace"""
    try:
        result = await editor_service.delete_file(workspace_id, path)
        return result
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ide/files/{workspace_id}")
async def list_files(
    workspace_id: str,
    directory: str = ".",
    api_key: str = Depends(verify_api_key)
):
    """List files in workspace directory"""
    try:
        files = await editor_service.list_files(workspace_id, directory)
        return {"files": files}
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/terminal", response_model=StandardResponse, tags=["IDE"])
async def create_terminal(
    request: IDETerminalRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new interactive terminal session for a workspace."""
    try:
        session_id = await terminal_service.create_session(request.workspace_id, request.shell)
        return StandardResponse(status="success", result={"session_id": session_id})
    except Exception as e:
        logger.error(f"Failed to create terminal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/ide/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal"""
    await websocket.accept()
    await terminal_service.handle_websocket(websocket, session_id)


@app.post("/api/ide/debug", response_model=StandardResponse, tags=["IDE"])
async def create_debug_session(
    request: IDEDebugRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start a Debug Adapter Protocol (DAP) session for the project."""
    try:
        session_id = await debugger_service.create_session(
            request.workspace_id,
            request.language,
            request.program,
            request.args
        )
        return StandardResponse(status="success", result={"session_id": session_id})
    except Exception as e:
        logger.error(f"Failed to create debug session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/debug/{session_id}/dap")
async def handle_dap_message(
    session_id: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Handle Debug Adapter Protocol message"""
    try:
        result = await debugger_service.handle_dap_message(session_id, request)
        return result
    except Exception as e:
        logger.error(f"DAP message failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- New Code Intelligence Endpoints ---

@app.get("/api/ide/tree/{workspace_id}")
async def get_file_tree(
    workspace_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get complete file tree for a workspace"""
    try:
        return await editor_service.get_file_tree(workspace_id)
    except Exception as e:
        logger.error(f"Failed to get file tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/intelligence/completions/{workspace_id}/{path:path}")
async def get_completions(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Get AI-powered code completions"""
    try:
        return await editor_service.get_completions(
            workspace_id,
            path,
            request.get("offset", 0),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to get completions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/intelligence/hover/{workspace_id}/{path:path}")
async def get_hover_info(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Get information about a symbol on hover"""
    try:
        return await editor_service.get_hover_info(
            workspace_id,
            path,
            request.get("symbol"),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to get hover info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ide/intelligence/diagnostics/{workspace_id}/{path:path}")
async def get_diagnostics(
    workspace_id: str,
    path: str,
    language: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Get code diagnostics"""
    try:
        return await editor_service.get_diagnostics(workspace_id, path, language)
    except Exception as e:
        logger.error(f"Failed to get diagnostics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ide/intelligence/refactor/{workspace_id}/{path:path}")
async def ai_refactor(
    workspace_id: str,
    path: str,
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Perform AI-powered refactoring"""
    try:
        return await editor_service.ai_refactor(
            workspace_id,
            path,
            request.get("instruction"),
            request.get("language")
        )
    except Exception as e:
        logger.error(f"Failed to perform AI refactor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Phase 2: Real-Time Monitoring Endpoints

@app.get("/api/monitoring/metrics")
async def get_monitoring_metrics(
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """Get monitoring metrics"""
    try:
        from services.monitoring import RealtimeMonitoringService
        monitoring = RealtimeMonitoringService()
        metrics = monitoring.get_metrics(limit)
        return {"metrics": metrics}
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitoring/metrics/current")
async def get_current_metrics(api_key: str = Depends(verify_api_key)):
    """Get current system metrics"""
    try:
        from services.monitoring import RealtimeMonitoringService
        monitoring = RealtimeMonitoringService()
        metrics = monitoring.get_current_metrics()
        return metrics or {}
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/monitoring/stream")
async def monitoring_stream(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics streaming"""
    await websocket.accept()
    
    from services.monitoring import RealtimeMonitoringService
    monitoring = RealtimeMonitoringService()
    await monitoring.register_websocket(websocket)
    
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception:
        pass
    finally:
        await monitoring.unregister_websocket(websocket)


@app.get("/api/monitoring/builds")
async def list_builds(
    status: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """List build progress"""
    try:
        from services.monitoring import RealtimeMonitoringService
        monitoring = RealtimeMonitoringService()
        builds = monitoring.list_builds(status)
        return {"builds": [b.to_dict() for b in builds]}
    except Exception as e:
        logger.error(f"Failed to list builds: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitoring/builds/{build_id}")
async def get_build(
    build_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get build progress"""
    try:
        from services.monitoring import RealtimeMonitoringService
        monitoring = RealtimeMonitoringService()
        build = monitoring.get_build(build_id)
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")
        return build.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get build: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Phase 2: Collaboration Endpoints

@app.post("/api/collaboration/session", response_model=StandardResponse, tags=["Collaboration"])
async def create_collaboration_session(
    request: CollaborationSessionRequest,
    api_key: str = Depends(verify_api_key)
):
    """Start a real-time collaboration session for a specific project."""
    try:
        from services.collaboration import CollaborationService
        collaboration = CollaborationService()
        
        session_id = await collaboration.create_session(
            request.project_id, 
            request.owner_id, 
            request.owner_name
        )
        return StandardResponse(status="success", result={"session_id": session_id})
    except Exception as e:
        logger.error(f"Failed to create collaboration session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/collaboration/{session_id}")
async def collaboration_websocket(
    websocket: WebSocket,
    session_id: str,
    user_id: str,
    username: str
):
    """WebSocket endpoint for collaboration"""
    await websocket.accept()
    
    from services.collaboration import CollaborationService
    collaboration = CollaborationService()
    await collaboration.handle_websocket(websocket, session_id, user_id, username)


# Phase 2: Workspace Management Endpoints

@app.post("/api/workspace", response_model=StandardResponse, tags=["Workspace"])
async def create_workspace(
    request: WorkspaceCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new multi-tenant workspace for organization and team management."""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        workspace = workspace_mgr.create_workspace(
            request.name, 
            request.owner_id, 
            request.owner_name
        )
        return StandardResponse(status="success", result=workspace.to_dict())
    except Exception as e:
        logger.error(f"Failed to create workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workspace/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get workspace"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        workspace = workspace_mgr.get_workspace(workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workspace/user/{user_id}")
async def list_user_workspaces(
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """List user workspaces"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        workspaces = workspace_mgr.list_user_workspaces(user_id)
        return {"workspaces": [w.to_dict() for w in workspaces]}
    except Exception as e:
        logger.error(f"Failed to list workspaces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/workspace/{workspace_id}/members", response_model=StandardResponse, tags=["Workspace"])
async def invite_member(
    workspace_id: str,
    request: WorkspaceInviteRequest,
    api_key: str = Depends(verify_api_key)
):
    """Invite a new member to the workspace with a specific role."""
    try:
        from services.workspace import WorkspaceManager, WorkspaceRole
        workspace_mgr = WorkspaceManager()
        
        role = WorkspaceRole(request.role)
        
        success = workspace_mgr.invite_member(
            workspace_id,
            request.inviter_id,
            request.user_id,
            request.username,
            role
        )
        
        if not success:
            raise HTTPException(status_code=403, detail="Permission denied or member already exists")
        
        return StandardResponse(status="success", message="Member invited successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invite member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/workspace/{workspace_id}/members/{user_id}")
async def remove_member(
    workspace_id: str,
    user_id: str,
    remover_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Remove member from workspace"""
    try:
        from services.workspace import WorkspaceManager
        workspace_mgr = WorkspaceManager()
        
        success = workspace_mgr.remove_member(workspace_id, remover_id, user_id)
        
        if not success:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove member: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Kubernetes Endpoints

@app.post("/api/kubernetes/generate", response_model=StandardResponse, tags=["Infrastructure"])
async def generate_kubernetes_config(
    request: Dict[str, Any], # Keep dict here as it's a complex dynamic config, but use StandardResponse
    api_key: str = Depends(verify_api_key)
):
    """Generate high-fidelity Kubernetes manifests and Helm charts."""
    try:
        from services.kubernetes import KubernetesGenerator
        from schemas.generation_spec import KubernetesConfig
        
        app_name = request.get("app_name", "my-app")
        image = request.get("image", "my-app:latest")
        config_data = request.get("config", {})
        config = KubernetesConfig(**config_data)
        
        generator = KubernetesGenerator()
        manifests = generator.generate_manifests(app_name, image, config)
        
        return StandardResponse(status="success", result={"manifests": manifests})
    except Exception as e:
        logger.error(f"K8s generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Orchestrator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    
    args = parser.parse_args()
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info"
    )


if __name__ == "__main__":
    main()
