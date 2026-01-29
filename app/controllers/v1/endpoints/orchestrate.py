"""Orchestration API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime

from ....core.database import get_db
from ....middleware.auth import require_auth
from ....core.security.prompt_validator import security_validator as prompt_validator
from ....core.billing import TokenBudgetManager
from ....core.agent_manager import agent_manager
from core.container import container
from ....schemas.v1.orchestration import (
    OrchestrationRequest, 
    OrchestrationResponse, 
    ExecutionStatusEnum
)

router = APIRouter(prefix="/orchestrate", tags=["Orchestration"])

@router.post("/", response_model=OrchestrationResponse, status_code=status.HTTP_202_ACCEPTED)
async def orchestrate(
    request: OrchestrationRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Initiates an AI orchestration task."""
    
    # 1. Prompt Injection Validation (V2.0 Hardened)
    is_safe, details = prompt_validator.validate(request.prompt, user_id=user["sub"])
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "SECURITY_VIOLATION",
                "message": "Security compliance check failed",
                "details": details
            }
        )
    
    # 2. Token Budget Check (simplified estimation)
    if container.monitoring_service:
        has_budget = await container.monitoring_service.check_budget(user["sub"], estimated_tokens=1000)
        if not has_budget:
            raise HTTPException(
                status_code=422,
                detail={"code": "QUOTA_EXCEEDED", "message": "Token budget exceeded for today"}
            )
    
    # 3. Create Execution Record (ID generation for now)
    execution_id = f"exec_{uuid.uuid4().hex}"
    
    # 4. Start Orchestration (Placeholder for background task)
    # BackgroundTask(run_orchestration, execution_id, request)
    
    return OrchestrationResponse(
        success=True,
        request_id=str(uuid.uuid4()),
        execution_id=execution_id,
        status=ExecutionStatusEnum.PENDING,
        message="Orchestration task accepted and queued",
        result_url=f"/api/v1/executions/{execution_id}",
        websocket_url=f"wss://api.ai-orchestrator.com/v1/executions/{execution_id}/stream",
        estimated_duration_ms=5000
    )

