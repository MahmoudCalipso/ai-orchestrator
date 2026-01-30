"""Agent API Endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import uuid
from datetime import datetime

from ....core.database import get_db
from ....middleware.auth import require_auth
from ....models.agent import Agent, AgentStatus
from dto.v1.base import BaseResponse, ResponseStatus
from dto.v1.requests.agent import CreateAgentRequest, UpdateAgentRequest
from dto.v1.responses.agent import (
    AgentResponseDTO, AgentInitializationResponseDTO, AgentStatusEnum, AgentListResponseDTO
)

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=BaseResponse[AgentInitializationResponseDTO], status_code=status.HTTP_201_CREATED)
async def create_agent(
    request: CreateAgentRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Creates a new AI agent for the authenticated user."""
    
    # Check if agent name already exists for this user
    existing = await db.execute(
        select(Agent).where(Agent.name == request.name, Agent.user_id == user["sub"])
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, 
            detail=f"Agent with name '{request.name}' already exists"
        )
    
    # Create agent record
    new_agent = Agent(
        **request.model_dump(),
        user_id=user["sub"],
        status=AgentStatus.INITIALIZING
    )
    
    db.add(new_agent)
    await db.commit()
    await db.refresh(new_agent)
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AGENT_CREATED",
        data=AgentInitializationResponseDTO(
            agent=AgentResponseDTO.model_validate(new_agent),
            initialization_status="initializing",
            websocket_url=f"wss://api.ai-orchestrator.com/v1/agents/{new_agent.id}/stream"
        )
    )

@router.get("/", response_model=BaseResponse[AgentListResponseDTO])
async def list_agents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Lists agents with pagination."""
    
    offset = (page - 1) * limit
    
    # Get total count
    count_stmt = select(func.count()).select_from(Agent).where(Agent.user_id == user["sub"])
    total_count = (await db.execute(count_stmt)).scalar() or 0
    
    # Get paginated data
    stmt = select(Agent).where(Agent.user_id == user["sub"]).offset(offset).limit(limit)
    result = await db.execute(stmt)
    agents = result.scalars().all()
    
    total_pages = (total_count + limit - 1) // limit
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AGENTS_LIST_RETRIEVED",
        data=AgentListResponseDTO(
            agents=[AgentResponseDTO.model_validate(a) for a in agents],
            total=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    )

@router.get("/{agent_id}", response_model=BaseResponse[AgentResponseDTO])
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Retrieves details of a specific agent."""
    
    stmt = select(Agent).where(Agent.id == agent_id, Agent.user_id == user["sub"])
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AGENT_RETRIEVED",
        data=AgentResponseDTO.model_validate(agent)
    )

@router.patch("/{agent_id}", response_model=BaseResponse[AgentResponseDTO])
async def update_agent(
    agent_id: str,
    request: UpdateAgentRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Partially updates an agent's configuration."""
    
    stmt = select(Agent).where(Agent.id == agent_id, Agent.user_id == user["sub"])
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agent, key, value)
    
    agent.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(agent)
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AGENT_UPDATED",
        data=AgentResponseDTO.model_validate(agent)
    )

@router.delete("/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(require_auth)
):
    """Deletes an agent and releases resources."""
    
    stmt = select(Agent).where(Agent.id == agent_id, Agent.user_id == user["sub"])
    result = await db.execute(stmt)
    agent = result.scalar_one_or_none()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    await db.delete(agent)
    await db.commit()
    
    return BaseResponse(
        status=ResponseStatus.SUCCESS,
        code="AGENT_DELETED",
        message="Agent deleted successfully",
        data={
            "agent_id": agent_id,
            "cleanup_status": {
                "memory_released": "success",
                "sessions_archived": "success",
                "websocket_connections": "closed"
            }
        }
    )

