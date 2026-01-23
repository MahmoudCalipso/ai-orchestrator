import os
import json
import logging
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

Base = declarative_base()

class UnifiedDatabaseManager:
    """
    Unified Database Manager for the AI Orchestrator.
    Handles connections to:
    1. PostgreSQL (Transactional Data)
    2. Redis (Caching & Real-time)
    3. MongoDB (Large Documents/Files)
    4. Qdrant (Vector Embeddings)
    """

    def __init__(self):
        # Clients
        self.pg_engine = None
        self.AsyncSessionLocal = None
        self.redis = None
        self.mongo = None
        self.mongo_db = None
        self.qdrant = None

        # Config
        self.pg_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://orchestrator:MA-120396@postgres:5432/ai_orchestrator")
        # Convert sync URL to async if needed
        if self.pg_url.startswith("postgresql://"):
            self.pg_url = self.pg_url.replace("postgresql://", "postgresql+asyncpg://")

        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.mongo_url = os.getenv("MONGO_URL", "mongodb://orchestrator:MA-120396@mongodb:27017")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")

    async def initialize(self):
        """Initialize all database connections"""
        logger.info("Initializing multi-database production stack...")

        # 1. PostgreSQL (SQLAlchemy Async)
        try:
            self.pg_engine = create_async_engine(
                self.pg_url,
                pool_size=20,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                echo=False
            )
            self.AsyncSessionLocal = async_sessionmaker(
                bind=self.pg_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            logger.info("✓ PostgreSQL (Async) connected")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")

        # 2. Redis
        try:
            self.redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            await self.redis.ping()
            logger.info("✓ Redis connected")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

        # 3. MongoDB
        try:
            self.mongo = AsyncIOMotorClient(self.mongo_url)
            self.mongo_db = self.mongo[os.getenv("MONGO_DB", "ai_orchestrator")]
            # Trigger a simple command to check connectivity
            await self.mongo.admin.command('ping')
            logger.info("✓ MongoDB connected")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

        # 4. Qdrant
        try:
            self.qdrant = AsyncQdrantClient(url=self.qdrant_url)
            # Check connectivity
            await self.qdrant.get_collections()
            logger.info("✓ Qdrant connected")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")

        logger.info("Database stack initialization complete.")

    async def close(self):
        """Cleanly close all database connections"""
        logger.info("Closing database connections...")
        if self.pg_engine:
            await self.pg_engine.dispose()
        if self.redis:
            await self.redis.close()
        if self.mongo:
            self.mongo.close()
        if self.qdrant:
            await self.qdrant.close()
        logger.info("✓ All databases disconnected")

    # Helper for Postgres Session (async context manager)
    async def get_pg_session(self):
        """Get a PostgreSQL session as an async context manager"""
        if not self.AsyncSessionLocal:
            raise RuntimeError("PostgreSQL not initialized")
        
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Global Instance
unified_db = UnifiedDatabaseManager()
