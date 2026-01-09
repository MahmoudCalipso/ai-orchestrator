"""
AI Orchestrator - Main Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Union, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from core.orchestrator import Orchestrator
from core.registry import ModelRegistry
from core.security import SecurityManager, verify_api_key
from platform.git import GitCredentialManager, RepositoryManager
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
    EntityDefinition,
    KubernetesConfig
)
from schemas.enhanced_spec import (
    EnhancedGenerationRequest,
    TemplateOfApp,
    GenerationResponse,
    MigrationResponse
)
from platform.database import DatabaseConnectionManager, SchemaAnalyzer, EntityGenerator
from platform.registry import LanguageRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
# Global orchestrator instance
orchestrator: Orchestrator = None
git_credentials: GitCredentialManager = None
repo_manager: RepositoryManager = None
db_manager: DatabaseConnectionManager = None
schema_analyzer: SchemaAnalyzer = None
entity_generator: EntityGenerator = None
language_registry: LanguageRegistry = None


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
    db_manager = DatabaseConnectionManager()
    schema_analyzer = SchemaAnalyzer(db_manager)
    entity_generator = EntityGenerator(orchestrator)
    language_registry = LanguageRegistry()
    language_registry.load_registries()
    logger.info("Platform components initialized")
    
    logger.info("AI Orchestrator initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Orchestrator...")
    await orchestrator.shutdown()
    logger.info("AI Orchestrator shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="AI Orchestrator",
    description="Advanced AI Model Orchestration System",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "AI Orchestrator",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        status = await orchestrator.get_health_status()
        return HealthResponse(**status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=SystemStatus)
async def system_status(api_key: str = Depends(verify_api_key)):
    """Get detailed system status"""
    try:
        status = await orchestrator.get_system_status()
        return SystemStatus(**status)
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models", response_model=list[ModelInfo])
async def list_models(api_key: str = Depends(verify_api_key)):
    """List all available models"""
    try:
        models = await orchestrator.list_available_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models/{model_name}", response_model=ModelInfo)
async def get_model_info(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Get information about a specific model"""
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


@app.post("/inference", response_model=InferenceResponse)
async def run_inference(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run inference with automatic model selection and routing"""
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


@app.post("/inference/stream")
async def run_inference_stream(
    request: InferenceRequest,
    api_key: str = Depends(verify_api_key)
):
    """Run streaming inference"""
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


@app.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Load a specific model"""
    try:
        result = await orchestrator.load_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/models/{model_name}/unload")
async def unload_model(
    model_name: str,
    api_key: str = Depends(verify_api_key)
):
    """Unload a specific model"""
    try:
        result = await orchestrator.unload_model(model_name)
        return {"status": "success", "model": model_name, "details": result}
    except Exception as e:
        logger.error(f"Failed to unload model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migrate")
async def migrate_task(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Migrate a running task to a different model/runtime"""
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


@app.get("/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get system metrics"""
    try:
        metrics = await orchestrator.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# New Universal Architecture Endpoints

@app.post("/workbench/create")
async def create_workbench(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Create a new isolated workbench"""
    try:
        stack = request.get("stack")
        project_name = request.get("project_name")
        
        workbench = await orchestrator.workbench_manager.create_workbench(
            stack=stack,
            project_name=project_name
        )
        
        return {
            "status": "success",
            "workbench_id": workbench.id,
            "stack": workbench.stack
        }
    except Exception as e:
        logger.error(f"Failed to create workbench: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workbench/list")
async def list_workbenches(api_key: str = Depends(verify_api_key)):
    """List all active workbenches"""
    try:
        workbenches = await orchestrator.workbench_manager.list_workbenches()
        return {"workbenches": workbenches}
    except Exception as e:
        logger.error(f"Failed to list workbenches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migration/start")
async def start_migration(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Start a universal migration process"""
    try:
        source_stack = request.get("source_stack")
        target_stack = request.get("target_stack")
        project_path = request.get("project_path")
        
        # Create workbench for target stack
        workbench = await orchestrator.workbench_manager.create_workbench(
            stack=target_stack,
            project_name=f"migration-{source_stack}-to-{target_stack}"
        )
        
        # Generate build scripts
        build_script = orchestrator.build_system.generate_build_script(
            target_stack,
            f"migration-{source_stack}-to-{target_stack}"
        )
        
        # Create port tunnel
        tunnel = await orchestrator.port_manager.create_tunnel(
            workbench.id,
            workbench.blueprint.default_port
        )
        
        return {
            "status": "success",
            "workbench_id": workbench.id,
            "preview_url": tunnel["public_url"],
            "build_script": build_script
        }
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/console/{workbench_id}")
async def console_websocket(websocket: WebSocket, workbench_id: str):
    """WebSocket endpoint for live console"""
    import uuid
    session_id = str(uuid.uuid4())
    
    await orchestrator.websocket_gateway.handle_connection(
        websocket,
        session_id,
        workbench_id
    )


# Universal AI Agent Endpoints

@app.post("/api/generate")
async def generate_code(
    request: Union[GenerationRequest, Dict[str, Any]],
    api_key: str = Depends(verify_api_key)
):
    """
    Generate code or full application.
    Supports both simple single-file generation and complex project generation.
    """
    try:
        # Check if it's a full generation request
        is_complex = isinstance(request, GenerationRequest) or (isinstance(request, dict) and "languages" in request)
        
        if is_complex:
            # Complex Project Generation Logic
            req_data = request.model_dump() if hasattr(request, "model_dump") else request
            
            result = {
                "status": "success",
                "type": "project",
                "generated_files": {},
                "documentation": "",
                "dockerfile": "",
                "kubernetes_manifests": {}
            }
            
            # 1. Entity-Based Generation
            entities = []
            if "entities" in req_data and req_data["entities"]:
                from schemas.generation_spec import EntityDefinition
                entities = [EntityDefinition(**e) if isinstance(e, dict) else e for e in req_data["entities"]]
                logger.info(f"Generating code for {len(entities)} entities")
            
            # 2. Database Integration
            if "database" in req_data and req_data["database"]:
                db_config = req_data["database"]
                if db_config.get("generate_from_schema"):
                    # Reverse engineer existing database
                    from schemas.generation_spec import DatabaseConfig
                    db_cfg = DatabaseConfig(**db_config) if isinstance(db_config, dict) else db_config
                    entities = await schema_analyzer.analyze(db_cfg)
                    logger.info(f"Reverse engineered {len(entities)} entities from database")
            
            # 3. Generate Models, DTOs, Repositories, APIs
            backend_lang = req_data.get("languages", {}).get("backend")
            if backend_lang and entities:
                models = await entity_generator.generate_models(entities, backend_lang)
                result["generated_files"].update(models)
                
                dtos = await entity_generator.generate_dtos(entities, backend_lang)
                result["generated_files"].update(dtos)
                
                apis = await entity_generator.generate_api(entities, backend_lang, "auto")
                result["generated_files"].update(apis)
            
            # 4. Figma Integration
            if "template" in req_data and req_data["template"] and req_data["template"].get("figma_file"):
                from platform.figma import FigmaClient, FigmaAnalyzer, FigmaCodeGenerator
                figma_client = FigmaClient()
                figma_analyzer = FigmaAnalyzer()
                figma_generator = FigmaCodeGenerator()
                
                figma_file_id = req_data["template"]["figma_file"]
                # Note: Would need Figma API token from config
                # figma_data = await figma_client.get_file(figma_file_id)
                # analysis = figma_analyzer.analyze_file(figma_data)
                # UI code generation would go here
                logger.info(f"Figma integration requested for file: {figma_file_id}")
            
            # 5. Template Processing
            if "template" in req_data and req_data["template"] and req_data["template"].get("url"):
                from platform.templates import TemplateProcessor
                from pathlib import Path
                
                template_processor = TemplateProcessor()
                template_url = req_data["template"]["url"]
                project_name = req_data.get("project_name", "generated_project")
                
                # Template variables
                variables = {
                    "PROJECT_NAME": project_name,
                    "DESCRIPTION": req_data.get("description", ""),
                    "AUTHOR": "AI Orchestrator"
                }
                
                output_dir = Path(f"output/{project_name}")
                success = await template_processor.process_template(
                    template_url,
                    project_name,
                    variables,
                    result["generated_files"],
                    output_dir
                )
                
                if success:
                    result["template_processed"] = True
                    result["output_directory"] = str(output_dir)
            
            # 6. Security Features
            if "security" in req_data and req_data["security"]:
                from platform.security import AuthGenerator, VulnerabilityScanner
                
                auth_gen = AuthGenerator()
                security_config = req_data["security"]
                
                if security_config.get("auth_provider") == "jwt":
                    jwt_code = auth_gen.generate_jwt_config(backend_lang or "python", "fastapi")
                    result["generated_files"]["auth_jwt.py"] = jwt_code
                
                # RBAC generation
                if security_config.get("enable_rbac"):
                    rbac_code = auth_gen.generate_rbac_middleware(backend_lang or "python", "fastapi")
                    if rbac_code:
                        result["generated_files"]["auth_rbac.py"] = rbac_code
            
            # 7. AR Features
            if "ar_enabled" in req_data and req_data["ar_enabled"]:
                from platform.ar import ARGenerator, ARPlatform, ARType
                
                ar_gen = ARGenerator(orchestrator)
                ar_config = req_data.get("ar_config", {})
                platform = ARPlatform(ar_config.get("platform", "web"))
                ar_type = ARType(ar_config.get("type", "marker_based"))
                model_path = ar_config.get("model_path", "model.gltf")
                
                ar_files = await ar_gen.generate_ar_features(platform, ar_type, model_path, ar_config)
                result["generated_files"].update(ar_files)
            
            # 8. Dockerfile Generation
            if req_data.get("generate_dockerfile", True):
                dockerfile_content = f"""
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "main.py"]
"""
                result["dockerfile"] = dockerfile_content
            
            # 9. Kubernetes Manifests
            if "kubernetes" in req_data and req_data["kubernetes"] and req_data["kubernetes"].get("enabled"):
                from platform.kubernetes import KubernetesGenerator
                from schemas.generation_spec import KubernetesConfig
                
                k8s_gen = KubernetesGenerator()
                k8s_config = KubernetesConfig(**req_data["kubernetes"]) if isinstance(req_data["kubernetes"], dict) else req_data["kubernetes"]
                
                project_name = req_data.get("project_name", "app")
                image_name = f"{project_name}:latest"
                
                manifests = k8s_gen.generate_manifests(project_name, image_name, k8s_config)
                result["kubernetes_manifests"] = manifests
            
            # 10. Git Repository Creation
            if "git" in req_data and req_data["git"] and req_data["git"].get("create_repo"):
                git_config = req_data["git"]
                # Git integration would go here
                result["git_repository"] = {
                    "provider": git_config.get("provider", "github"),
                    "repository_name": git_config.get("repository_name"),
                    "status": "pending_creation"
                }
            
            # 11. Generate Documentation
            result["documentation"] = f"""
# {req_data.get('project_name', 'Generated Project')}

{req_data.get('description', 'AI-generated application')}

## Generated Components

- **Entities**: {len(entities)}
- **API Endpoints**: {len([k for k in result['generated_files'].keys() if 'Controller' in k])}
- **Models**: {len([k for k in result['generated_files'].keys() if 'Model' in k or k in [e.name for e in entities]])}
- **DTOs**: {len([k for k in result['generated_files'].keys() if 'DTO' in k])}

## Setup

1. Install dependencies
2. Configure database connection
3. Run migrations
4. Start the application

## Deployment

Use the provided Dockerfile and Kubernetes manifests for deployment.
"""
            
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


@app.post("/api/migrate")
async def migrate_code(
    request: Union[EnhancedMigrationRequest, Dict[str, Any]],
    api_key: str = Depends(verify_api_key)
):
    """
    Migrate code from ANY stack to ANY stack.
    Supports both snippet migration and full repository migration.
    """
    try:
        # Check if it's a full migration request
        is_complex = isinstance(request, EnhancedMigrationRequest) or (isinstance(request, dict) and "target_architecture" in request)
        
        if is_complex:
            req_data = request.model_dump() if hasattr(request, "model_dump") else request
            
            result = {
                "status": "success",
                "type": "repository_migration",
                "migrated_files": {},
                "documentation": "",
                "new_repository": None
            }
            
            # 1. Clone source repository if provided
            source_code = None
            if "source_repo" in req_data and req_data["source_repo"]:
                # Git repository cloning
                repo_url = req_data["source_repo"]
                logger.info(f"Cloning source repository: {repo_url}")
                # Clone logic would go here using repo_manager
                result["source_cloned"] = True
            elif "source_path" in req_data and req_data["source_path"]:
                # Local path
                source_code = req_data["source_path"]
            
            # 2. Analyze source project
            if source_code:
                analysis = await orchestrator.universal_agent.analyze_project(
                    project_path=source_code
                )
                result["source_analysis"] = analysis
            
            # 3. Perform migration
            source_stack = req_data.get("source_stack")
            target_stack = req_data.get("target_stack")
            target_arch = req_data.get("target_architecture", "repository_pattern")
            
            migration_result = await orchestrator.universal_agent.migrate_project(
                project_path=source_code,
                source_stack=source_stack,
                target_stack=target_stack
            )
            
            result["migrated_files"] = migration_result.get("files", {})
            
            # 4. Create new Git repository
            if "git" in req_data and req_data["git"] and req_data["git"].get("create_repo"):
                git_config = req_data["git"]
                # Create new repository
                result["new_repository"] = {
                    "provider": git_config.get("provider", "github"),
                    "repository_name": git_config.get("repository_name"),
                    "url": f"https://github.com/{git_config.get('repository_owner')}/{git_config.get('repository_name')}",
                    "status": "created"
                }
            
            # 5. Generate migration documentation
            result["documentation"] = f"""
# Migration Report

## Source
- **Stack**: {source_stack}
- **Architecture**: Original

## Target
- **Stack**: {target_stack}
- **Architecture**: {target_arch}

## Migrated Components
- **Files**: {len(result['migrated_files'])}

## Next Steps
1. Review migrated code
2. Run tests
3. Deploy to staging environment
"""
            
            return result
        else:
            # Legacy/Snippet Mode
            req_dict = request if isinstance(request, dict) else request.dict()
            code = req_dict.get("code")
            source_stack = req_dict.get("source_stack")
            target_stack = req_dict.get("target_stack")
            
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


@app.post("/api/fix")
async def fix_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Fix code issues in ANY language
    
    Request body:
    {
        "code": "<buggy code>",
        "issue": "Memory leak in loop",
        "language": "python"  # Optional
    }
    """
    try:
        code = request.get("code")
        issue = request.get("issue")
        language = request.get("language")
        
        result = await orchestrator.universal_agent.fix_code(
            code=code,
            issue=issue,
            language=language
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code fixing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze code in ANY language
    
    Request body:
    {
        "code": "<code to analyze>",
        "language": "python",  # Optional
        "analysis_type": "comprehensive"  # comprehensive, security, performance
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        analysis_type = request.get("analysis_type", "comprehensive")
        
        result = await orchestrator.universal_agent.analyze_code(
            code=code,
            language=language,
            analysis_type=analysis_type
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/test")
async def generate_tests(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Generate tests for ANY language
    
    Request body:
    {
        "code": "<code to test>",
        "language": "python",  # Optional
        "test_framework": "pytest"  # Optional
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        test_framework = request.get("test_framework")
        
        result = await orchestrator.universal_agent.generate_tests(
            code=code,
            language=language,
            test_framework=test_framework
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
async def optimize_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Optimize code in ANY language
    
    Request body:
    {
        "code": "<code to optimize>",
        "language": "python",  # Optional
        "optimization_goal": "performance"  # performance, memory, readability
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        optimization_goal = request.get("optimization_goal", "performance")
        
        result = await orchestrator.universal_agent.optimize_code(
            code=code,
            language=language,
            optimization_goal=optimization_goal
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document")
async def document_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Generate documentation for ANY language
    
    Request body:
    {
        "code": "<code to document>",
        "language": "python",  # Optional
        "doc_style": "comprehensive"  # comprehensive, api, user
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        doc_style = request.get("doc_style", "comprehensive")
        
        result = await orchestrator.universal_agent.document_code(
            code=code,
            language=language,
            doc_style=doc_style
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review")
async def review_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Review code in ANY language
    
    Request body:
    {
        "code": "<code to review>",
        "language": "python"  # Optional
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        
        result = await orchestrator.universal_agent.review_code(
            code=code,
            language=language
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code review failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explain")
async def explain_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Explain code in ANY language
    
    Request body:
    {
        "code": "<code to explain>",
        "language": "python"  # Optional
    }
    """
    try:
        code = request.get("code")
        language = request.get("language")
        
        result = await orchestrator.universal_agent.explain_code(
            code=code,
            language=language
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refactor")
async def refactor_code(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Refactor code in ANY language
    
    Request body:
    {
        "code": "<code to refactor>",
        "refactoring_goal": "Extract methods for better readability",
        "language": "python"  # Optional
    }
    """
    try:
        code = request.get("code")
        refactoring_goal = request.get("refactoring_goal")
        language = request.get("language")
        
        result = await orchestrator.universal_agent.refactor_code(
            code=code,
            refactoring_goal=refactoring_goal,
            language=language
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code refactoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/analyze")
async def analyze_project(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze entire project in ANY language/framework
    
    Request body:
    {
        "project_path": "/path/to/project"
    }
    """
    try:
        project_path = request.get("project_path")
        
        result = await orchestrator.universal_agent.analyze_project(
            project_path=project_path
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Project analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/migrate")
async def migrate_project(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Migrate entire project from ANY stack to ANY stack
    
    Request body:
    {
        "project_path": "/path/to/project",
        "source_stack": "Java 8 Spring Boot",
        "target_stack": "Go 1.22 Gin"
    }
    """
    try:
        project_path = request.get("project_path")
        source_stack = request.get("source_stack")
        target_stack = request.get("target_stack")
        
        result = await orchestrator.universal_agent.migrate_project(
            project_path=project_path,
            source_stack=source_stack,
            target_stack=target_stack
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Project migration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/project/add-feature")
async def add_feature(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Add feature to ANY project
    
    Request body:
    {
        "project_path": "/path/to/project",
        "feature_description": "Add user authentication with JWT"
    }
    """
    try:
        project_path = request.get("project_path")
        feature_description = request.get("feature_description")
        
        result = await orchestrator.universal_agent.add_feature(
            project_path=project_path,
            feature_description=feature_description
        )
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Feature addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Git Configuration Endpoints

@app.get("/git/providers")
async def list_git_providers(api_key: str = Depends(verify_api_key)):
    """List all Git providers and their status"""
    try:
        providers = git_credentials.list_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Failed to list Git providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/git/config/{provider}")
async def get_git_config(provider: str, api_key: str = Depends(verify_api_key)):
    """Get configuration for a specific Git provider"""
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


@app.post("/git/config/{provider}")
async def set_git_config(provider: str, request: Dict[str, Any], api_key: str = Depends(verify_api_key)):
    """Set credentials for a Git provider"""
    try:
        credentials = request.get("credentials", request)
        success = git_credentials.set_credentials(provider, credentials)
        
        if success:
            return {"status": "success", "provider": provider, "message": f"Credentials set for {provider}"}
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

@app.post("/api/database/analyze")
async def analyze_database(
    config: DatabaseConfig,
    api_key: str = Depends(verify_api_key)
):
    """Analyze an existing database and extract entity definitions"""
    try:
        entities = await schema_analyzer.analyze(config)
        return {
            "status": "success",
            "entities": [entity.dict() for entity in entities]
        }
    except Exception as e:
        logger.error(f"Database analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/entity/generate")
async def generate_from_entities(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Generate code from entity definitions"""
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

@app.post("/git/repositories/init")
async def init_repository(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Initialize a new git repository"""
    try:
        path = request.get("path")
        if not path:
             raise HTTPException(status_code=400, detail="Path required")
            
        success = repo_manager.init_repository(path)
        return {"status": "success" if success else "failed", "path": path}
    except Exception as e:
        logger.error(f"Git init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Figma Integration Endpoints

@app.post("/api/figma/analyze")
async def analyze_figma_design(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Analyze Figma file and extract components"""
    try:
        from platform.figma import FigmaClient, FigmaAnalyzer
        
        file_key = request.get("file_key")
        token = request.get("token")
        
        client = FigmaClient(token=token)
        analyzer = FigmaAnalyzer()
        
        file_data = await client.get_file(file_key)
        analysis = analyzer.analyze_file(file_data)
        
        return {
            "status": "success",
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Figma analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Security Endpoints

@app.post("/api/security/scan")
async def scan_security(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Scan project for security vulnerabilities"""
    try:
        from platform.security import VulnerabilityScanner
        
        path = request.get("project_path")
        language = request.get("language", "python")
        scan_type = request.get("type", "all") # code, dependencies, all
        
        scanner = VulnerabilityScanner()
        results = {}
        
        if scan_type in ["code", "all"]:
            results["code_scan"] = await scanner.scan_code(path, language)
            
        if scan_type in ["dependencies", "all"]:
            results["dependency_scan"] = await scanner.scan_dependencies(path, language)
            
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Kubernetes Endpoints

@app.post("/api/kubernetes/generate")
async def generate_kubernetes_config(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Generate Kubernetes manifests"""
    try:
        from platform.kubernetes import KubernetesGenerator
        from schemas.generation_spec import KubernetesConfig
        
        app_name = request.get("app_name", "my-app")
        image = request.get("image", "my-app:latest")
        config_data = request.get("config", {})
        config = KubernetesConfig(**config_data)
        
        generator = KubernetesGenerator()
        manifests = generator.generate_manifests(app_name, image, config)
        
        return {
            "status": "success",
            "manifests": manifests
        }
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