"""
SQLAlchemy base models and session management
"""
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os
import sys

# SECURITY: No default credentials - must be set via environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable is required")
    print("Please set it in your .env file")
    sys.exit(1)

class Base(DeclarativeBase):
    pass

# Use shared engine and session from platform core
from platform_core.database import engine, SessionLocal, Base

def get_db():
    """Database session dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
