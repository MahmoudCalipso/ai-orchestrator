import os
import json
import logging
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import AsyncQdrantClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from tenacity import retry, stop_after_attempt, wait_exponential

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

        # Config - SECURITY: All credentials must come from environment
        self.pg_url = os.getenv("DATABASE_URL")
        if not self.pg_url:
            logger.error("DATABASE_URL environment variable is required")
            raise ValueError("DATABASE_URL must be set in environment")
        
        # Convert sync URL to async if needed
        if self.pg_url.startswith("postgresql://"):
            self.pg_url = self.pg_url.replace("postgresql://", "postgresql+asyncpg://")

        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.mongo_url = os.getenv("MONGO_URL")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")

    async def initialize(self):
        """Initialize all database connections with retries and graceful failure handling"""
        logger.info("Initializing multi-database production stack...")

        # 1. PostgreSQL (SQLAlchemy Async) - CRITICAL
        try:
            await self._init_postgres()
            logger.info("✓ PostgreSQL (Async) initialized")
        except Exception as e:
            logger.critical(f"CRITICAL: Failed to connect to PostgreSQL: {e}")
            # We don't raise here but this database is essential for most operations

        # 2. Redis - SEMI-CRITICAL (used for auth/rate-limiting)
        try:
            await self._init_redis()
            logger.info("✓ Redis connected")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

        # 3. MongoDB - OPTIONAL
        if self.mongo_url:
            try:
                await self._init_mongo()
                logger.info("✓ MongoDB connected")
            except Exception as e:
                logger.warning(f"Optional MongoDB initialization failed: {e}")
        else:
            logger.info("MongoDB skip: No MONGO_URL provided")

        # 4. Qdrant - OPTIONAL
        if self.qdrant_url:
            try:
                await self._init_qdrant()
                logger.info("✓ Qdrant connected")
            except Exception as e:
                logger.warning(f"Optional Qdrant initialization failed: {e}")
        else:
            logger.info("Qdrant skip: No QDRANT_URL provided")

        logger.info("Database stack initialization attempt complete.")

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _init_postgres(self):
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
        # Test connection
        async with self.pg_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    async def _init_redis(self):
        self.redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True
        )
        await self.redis.ping()

    async def _init_mongo(self):
        self.mongo = AsyncIOMotorClient(self.mongo_url, serverSelectionTimeoutMS=5000)
        self.mongo_db = self.mongo[os.getenv("MONGO_DB", "ai_orchestrator")]
        await self.mongo.admin.command('ping')

    async def _init_qdrant(self):
        self.qdrant = AsyncQdrantClient(url=self.qdrant_url, timeout=5)
        await self.qdrant.get_collections()

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
