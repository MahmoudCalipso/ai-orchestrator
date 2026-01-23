from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, DateTime, JSON, Integer, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from platform_core.database import Base

class NeuralMemory(Base):
    """
    Neural Memory L1 Persistence (PostgreSQL)
    Stores context, patterns, and preferences.
    """
    __tablename__ = "neural_memory"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, index=True, nullable=True) # Optional for now
    memory_type = Column(String(50), nullable=False, index=True) # 'context', 'pattern', 'preference'
    content = Column(JSON, nullable=False)
    confidence_score = Column(Numeric, default=1.0)
    accessed_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<NeuralMemory {self.memory_type}:{self.id}>"

class UsageMetric(Base):
    """System-wide usage metrics per user"""
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Numeric)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON, name="metadata")

class Project(Base):
    """Generated Projects Tracking"""
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tech_stack = Column(JSON, nullable=False)
    status = Column(String(50), default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON, name="metadata")
