"""
User Project Models
Database models for user project management
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base
from datetime import datetime
import uuid


from platform_core.auth.models import User
from dto.v1.schemas.enums import ProjectStatus, BuildStatus, RunStatus, WorkflowStatus
from sqlalchemy.orm import relationship, backref

class UserProject(Base):
    """User project model for tracking user-owned projects"""
    __tablename__ = "user_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    project_name = Column(String(255), nullable=False)
    description = Column(Text)
    git_repo_url = Column(String(500))
    git_branch = Column(String(100), default="main")
    local_path = Column(String(500))
    status = Column(String(50), default=ProjectStatus.ACTIVE.value, index=True)
    language = Column(String(50), index=True)
    framework = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_opened_at = Column(DateTime, index=True)
    build_status = Column(String(50), default=BuildStatus.PENDING.value, index=True)
    run_status = Column(String(50), default=RunStatus.STOPPED.value, index=True)
    extra_metadata = Column(JSONB)
    
    # Relationships
    sessions = relationship("ProjectSession", backref="project", cascade="all, delete-orphan")
    updates = relationship("ProjectUpdate", backref="project", cascade="all, delete-orphan")
    workflow_executions = relationship("WorkflowExecution", backref="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )


class ProjectSession(Base):
    """Project session model for tracking active IDE sessions"""
    __tablename__ = "project_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    workspace_id = Column(String(255))
    git_commit_hash = Column(String(40))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    status = Column(String(50), default="active")  # active, closed


class ProjectUpdate(Base):
    """Project update history model"""
    __tablename__ = "project_updates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    update_type = Column(String(50))  # ai-chat, ai-inline, manual
    description = Column(Text)
    files_changed = Column(JSONB)
    ai_prompt = Column(Text)
    git_commit_hash = Column(String(40))
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkflowExecution(Base):
    """Workflow execution tracking"""
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    workflow_type = Column(String(50))  # update-push-build-run, build-run, etc.
    steps = Column(JSONB)  # List of steps with status
    current_step = Column(String(50))
    status = Column(String(50), default=WorkflowStatus.PENDING.value, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    error_message = Column(Text)
    logs = Column(JSONB)

    def __repr__(self):
        return f"<WorkflowExecution {self.workflow_type} ({self.status})>"
