"""Aggregate router for v1 API."""
from fastapi import APIRouter
from .endpoints import agents, orchestrate, auth, projects, ai, services

api_router = APIRouter()
api_router.include_router(agents.router)
api_router.include_router(orchestrate.router)
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(ai.router)
api_router.include_router(services.git_router)
api_router.include_router(services.ide_router)
api_router.include_router(services.workspace_router)
api_router.include_router(services.system_router)
api_router.include_router(services.storage_router)
api_router.include_router(services.monitoring_router)
api_router.include_router(services.tools_router)
api_router.include_router(services.registry_router)
