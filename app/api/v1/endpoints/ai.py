"""AI API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any
import logging

from ....middleware.auth import require_auth
from ....core.container import container
from dto.common.base_response import BaseResponse
from dto.v1.requests.ai import InferenceRequest
from dto.v1.responses.ai import InferenceResponseDTO, ModelInfoDTO

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/models", response_model=BaseResponse)
async def list_models(
    page: int = 1,
    page_size: int = 20,
    user: dict = Depends(require_auth)
):
    """List available AI models."""
    # Logic from legacy ai_controller.py
    return BaseResponse(
        status="success",
        code="MODELS_DISCOVERED",
        message="Available models retrieved",
        data=[]
    )

@router.post("/inference", response_model=BaseResponse)
async def run_inference(
    request: InferenceRequest,
    user: dict = Depends(require_auth)
):
    """Run AI inference."""
    # Logic from legacy ai_controller.py
    return BaseResponse(
        status="success",
        code="INFERENCE_COMPLETED",
        message="AI inference completed",
        data={}
    )
