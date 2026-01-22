"""
Tools Controller
Handles external tools integrations: Figma, Kubernetes, Security, and Lifecycle.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from schemas.api_spec import (
    StandardResponse, FigmaAnalyzeRequest, SecurityScanRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tools"])

@router.post("/api/figma/analyze", response_model=StandardResponse)
async def analyze_figma_design(
    request: FigmaAnalyzeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze Figma design for code generation."""
    try:
        # Import locally if not in container or just use logic
        # Assuming FigmaAnalyzer is available
        from services.tools.figma_analyzer import FigmaAnalyzer
        analyzer = FigmaAnalyzer()
        result = await analyzer.analyze(request.file_key, request.token)
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Figma analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/kubernetes/generate", response_model=StandardResponse)
async def generate_kubernetes_config(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Generate Kubernetes manifests."""
    try:
        from services.tools.k8s_generator import KubernetesGenerator
        generator = KubernetesGenerator()
        result = await generator.generate(request.get("project_id"), request.get("config"))
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"K8s generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/security/scan", response_model=StandardResponse)
async def security_scan(
    request: SecurityScanRequest,
    api_key: str = Depends(verify_api_key)
):
    """Perform security scan."""
    try:
        from services.tools.security_scanner import SecurityScanner
        scanner = SecurityScanner()
        result = await scanner.scan(request.target, request.scan_type)
        return StandardResponse(status="success", result=result)
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/lifecycle/execute")
async def execute_lifecycle(
    project_id: str,
    stack: str,
    git_sync: bool = False,
    repo_name: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Execute E2E Project Lifecycle"""
    try:
        context = {
            "type": "finalization",
            "project_id": project_id,
            "stack": stack,
            "git_sync": git_sync,
            "repo_name": repo_name
        }
        
        if container.orchestrator and container.orchestrator.lead_architect:
            result = await container.orchestrator.lead_architect.act(
                f"Finalize project {project_id} for the user.",
                context
            )
            return result
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Lifecycle execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
