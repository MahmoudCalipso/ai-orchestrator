"""
SQLAlchemy base models and session management
"""
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os

# Default to PostgreSQL
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:MA-120396@127.0.0.1:5432/ai_orchestrator")

class Base(DeclarativeBase):
    pass

# Use shared engine and session from platform core
from platform_core.database import engine, SessionLocal, Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
