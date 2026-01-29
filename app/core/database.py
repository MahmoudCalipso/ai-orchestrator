"""Async database layer - MUST USE for all DB operations."""
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncSession, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, text
from sqlalchemy.pool import QueuePool
from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)

class DatabaseManager:
    """Manages async database connections with optimized pooling."""
    
    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.async_session_maker = None
        
    def initialize(self, database_url: str = None):
        if database_url is None:
            database_url = os.getenv(
                "DATABASE_URL", 
                "postgresql+asyncpg://user:pass@localhost/ai_orchestrator"
            )
        
        # Convert sync URL to async
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", 
                "postgresql+asyncpg://", 
                1
            )
        
        # Advanced V2.0 configuration for Military-Grade Resilience
        self.engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=30,  # Specific to V2.0 requirements
            pool_timeout=30,
            pool_recycle=1800,  # Reduced recycle time for freshness
            pool_pre_ping=True,
            echo=False,
            future=True,
            connect_args={
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "ai_orchestrator",
                    "jit": "off"
                }
            }
        )
        
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        logger.info("Database engine initialized with asyncpg")
        
    async def create_tables(self):
        async with self.engine.begin() as conn:
            # Note: In production, use migrations (alembic) instead
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()
    
    def get_pool_status(self) -> dict:
        """Returns connection pool metrics for health checks."""
        if not self.engine:
            return {"status": "uninitialized"}
        pool = self.engine.pool
        return {
            "size": pool.size(),
            "checkedin": pool.checkedin(),
            "checkedout": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": pool._max_overflow,
            "saturation": (pool.checkedout() / (pool.size() + pool._max_overflow)) * 100 if (pool.size() + pool._max_overflow) > 0 else 0
        }
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized")
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

db_manager = DatabaseManager()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for routes."""
    async with db_manager.session() as session:
        yield session
