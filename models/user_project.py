"""
User Project Models
Database models for user project management
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


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
    status = Column(String(50), default="active")  # active, archived, building, running
    language = Column(String(50))
    framework = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_opened_at = Column(DateTime)
    build_status = Column(String(50))  # success, failed, pending, building
    run_status = Column(String(50))  # running, stopped, crashed
    metadata = Column(JSONB)
    
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "project_name": self.project_name,
            "description": self.description,
            "git_repo_url": self.git_repo_url,
            "git_branch": self.git_branch,
            "local_path": self.local_path,
            "status": self.status,
            "language": self.language,
            "framework": self.framework,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_opened_at": self.last_opened_at.isoformat() if self.last_opened_at else None,
            "build_status": self.build_status,
            "run_status": self.run_status,
            "metadata": self.metadata
        }


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
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "git_commit_hash": self.git_commit_hash,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "status": self.status
        }


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
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": self.user_id,
            "update_type": self.update_type,
            "description": self.description,
            "files_changed": self.files_changed,
            "ai_prompt": self.ai_prompt,
            "git_commit_hash": self.git_commit_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class WorkflowExecution(Base):
    """Workflow execution tracking"""
    __tablename__ = "workflow_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    workflow_type = Column(String(50))  # update-push-build-run, build-run, etc.
    steps = Column(JSONB)  # List of steps with status
    current_step = Column(String(50))
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    logs = Column(JSONB)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": self.user_id,
            "workflow_type": self.workflow_type,
            "steps": self.steps,
            "current_step": self.current_step,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "logs": self.logs
        }
