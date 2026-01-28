"""Dependency injection container."""
import os
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import redis.asyncio as redis
from .database import db_manager, DatabaseManager
from .agent_manager import agent_manager, AgentManager

class Container(containers.DeclarativeContainer):
    """Service container for dependency injection."""
    
    config = providers.Configuration()
    
    # Database Manager
    db_manager = providers.Singleton(DatabaseManager)
    
    # Agent Manager
    agent_manager = providers.Singleton(AgentManager)
    
    # Redis Client
    redis_client = providers.Singleton(
        redis.from_url,
        url=config.database.redis_url,
        decode_responses=True
    )
    
    # Services (Placeholders for now)
    # ai_service = providers.Factory(...)
    # project_service = providers.Factory(...)

# Global container instance
container = Container()

def setup_container():
    """Configure the container with environment variables."""
    container.config.database.redis_url.from_env("REDIS_URL", "redis://localhost:6379")
    container.config.database.postgres_url.from_env("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/ai_orchestrator")
    
    # Initialize the actual db_manager (singleton)
    # This might be redundant if we use the one from container, 
    # but the spec uses a global db_manager.
    db_manager.initialize(container.config.database.postgres_url())
    
    return container
