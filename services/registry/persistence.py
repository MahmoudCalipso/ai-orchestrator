"""
Database models for persisting framework and language metadata
"""
from sqlalchemy import Column, String, JSON, DateTime, Integer
from datetime import datetime
from services.database.base import Base, engine

class FrameworkMetadata(Base):
    __tablename__ = "framework_metadata"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(50), index=True)
    framework = Column(String(50), index=True)
    latest_version = Column(String(20))
    lts_version = Column(String(20), nullable=True)
    versions = Column(JSON)  # List of strings
    architectures = Column(JSON)  # List of strings
    best_practices = Column(JSON)  # List of strings
    required_packages = Column(JSON)  # List of strings
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        unique_constraints = ["language", "framework"]

# Create tables
Base.metadata.create_all(bind=engine)
