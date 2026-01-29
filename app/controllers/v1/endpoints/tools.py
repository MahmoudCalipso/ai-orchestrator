"""
Tools Controller
Handles external tools integrations: Figma, Kubernetes, Security, and Lifecycle.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from core.security import verify_api_key
from core.container import container
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.responses.supplemental import FigmaAnalysisResponseDTO
from dto.v1.requests.git import (
    GitConfigUpdate, GitRepoInit, GitRemoteCreate,
    GitBranchCreate, GitCommitRequest, GitConflictResolve,
    GitMergeRequest
)
from dto.v1.requests.generation import FigmaAnalyzeRequest, SecurityScanRequest
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Tools"])

@router.post("/api/figma/analyze", response_model=BaseResponse[FigmaAnalysisResponseDTO])
async def analyze_figma_design(
    request: FigmaAnalyzeRequest,
    api_key: str = Depends(verify_api_key)
):
    """Analyze Figma design for code generation using AI."""
    try:
        from services.figma.analyzer import FigmaAnalyzer
        # Use orchestrator from container for AI power
        analyzer = FigmaAnalyzer(orchestrator=container.orchestrator)
        result = await analyzer.analyze_file(request.file_key) # Fixed access to request
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="FIGMA_ANALYSIS_COMPLETE",
            message="Figma design analyzed successfully",
            data=FigmaAnalysisResponseDTO(**result)
        )
    except Exception as e:
        logger.error(f"Figma analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/kubernetes/generate", response_model=BaseResponse[Dict[str, Any]])
async def generate_kubernetes_config(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """Generate Kubernetes manifests with AI refinement."""
    try:
        from services.kubernetes.manifest_generator import KubernetesGenerator
        generator = KubernetesGenerator(orchestrator=container.orchestrator)
        result = await generator.generate_manifests(
            request.get("app_name"), 
            request.get("image"), 
            request.get("config")
        )
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="K8S_CONFIG_GENERATED",
            data={"manifests": result}
        )
    except Exception as e:
        logger.error(f"K8s generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/security/scan", response_model=BaseResponse[Dict[str, Any]])
async def security_scan(
    request: SecurityScanRequest,
    api_key: str = Depends(verify_api_key)
):
    """Perform security scan with AI remediation."""
    try:
        from services.security.vulnerability_scanner import VulnerabilityScanner
        scanner = VulnerabilityScanner(orchestrator=container.orchestrator)
        result = await scanner.scan_code(request.project_path, request.language)
        return BaseResponse(
            status=ResponseStatus.SUCCESS,
            code="SECURITY_SCAN_COMPLETE",
            data={"vulnerabilities": result}
        )
    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/lifecycle/execute", response_model=BaseResponse[Dict[str, Any]])
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
            return BaseResponse(
                status=ResponseStatus.SUCCESS,
                code="LIFECYCLE_EXECUTED",
                data=result
            )
        raise HTTPException(status_code=503, detail="Orchestrator not ready")
    except Exception as e:
        logger.error(f"Lifecycle execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

