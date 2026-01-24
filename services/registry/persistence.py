"""
Database models for persisting framework and language metadata
"""
from sqlalchemy import Column, String, JSON, DateTime, Integer
from datetime import datetime
from services.database.base import Base, engine

class LanguageMetadata(Base):
    __tablename__ = "language_metadata"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    logo_url = Column(String(255), nullable=True)
    description = Column(String(500), nullable=True)
    update_source = Column(String(255), nullable=True) # e.g. "pypi", "npm"
    update_identifier = Column(String(255), nullable=True) # e.g. "python"
    is_compiled = Column(JSON, default=False)

class DatabaseMetadata(Base):
    __tablename__ = "database_metadata"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    logo_url = Column(String(255), nullable=True)
    db_type = Column(String(20)) # SQL, NoSQL, Vector, Graph
    latest_version = Column(String(20), nullable=True)
    update_source = Column(String(255), nullable=True)
    update_identifier = Column(String(255), nullable=True)

class FrameworkMetadata(Base):
    __tablename__ = "framework_metadata"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), index=True)
    framework = Column(String(50), index=True)
    logo_url = Column(String(255), nullable=True)
    latest_version = Column(String(20))
    lts_version = Column(String(20), nullable=True)
    versions = Column(JSON)  # List of strings
    architectures = Column(JSON)  # Detailed architecture guides
    best_practices = Column(JSON)  # Enhanced best practices
    required_packages = Column(JSON)  # List of strings
    update_source = Column(String(255), nullable=True) # e.g. "npm", "maven"
    update_identifier = Column(String(255), nullable=True) # e.g. "@angular/core"
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        unique_constraints = ["language", "framework"]

# Create tables (Force Recreate for Dev Session Stability)
try:
    # Drop existing to ensure column sync (Extreme Power 2026 Dev Mode)
    LanguageMetadata.__table__.drop(bind=engine, checkfirst=True)
    DatabaseMetadata.__table__.drop(bind=engine, checkfirst=True)
    FrameworkMetadata.__table__.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
except Exception as e:
    import logging
    logging.getLogger(__name__).error(f"Failed to create registry tables: {e}")

