"""
Shared Database Configuration
"""
import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load .env file
load_dotenv()
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment - REQUIRED for security
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is required")
    print("Please set it in your .env file or environment")
    sys.exit(1)

# Ensure sync URL for synchronous engine
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)


# For SQLite, we need to allow multithreading. For PostgreSQL, we add pooling.
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False  # Disable SQL echo in production
    )

from app.core.database import Base
# SessionLocal remains here for legacy sync components
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

