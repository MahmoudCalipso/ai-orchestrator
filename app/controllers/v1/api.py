"""Aggregate router for v1 API - Fully Consolidated."""
from fastapi import APIRouter

# Import all endpoint modules
from .endpoints import (
    agents, orchestrate, auth, projects, ai,
    admin, git, ide, workspace, monitoring,
    system, tools, registry, storage, enterprise,
    db_explorer, emulator
)

api_router = APIRouter()

# Core V2 Endpoints
api_router.include_router(agents.router)
api_router.include_router(orchestrate.router)

# Authentication & Authorization
api_router.include_router(auth.router)

# Project Management
api_router.include_router(projects.router)

# AI & ML Services
api_router.include_router(ai.router)

# Admin & System Management
api_router.include_router(admin.router)
api_router.include_router(system.router)
api_router.include_router(monitoring.router)

# Development Tools
api_router.include_router(git.router)
api_router.include_router(ide.router)
api_router.include_router(workspace.router)
api_router.include_router(tools.router)

# Infrastructure Services
api_router.include_router(registry.router)
api_router.include_router(storage.router)

# Enterprise Features
api_router.include_router(enterprise.router)

# Utilities
api_router.include_router(db_explorer.router)
api_router.include_router(emulator.router)
