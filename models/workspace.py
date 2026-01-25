"""
Workspace Database Models
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from platform_core.database import Base

class Workspace(Base):
    """Team Workspace model"""
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, nullable=False, index=True) # Linked to User.id but avoiding direct FK for simplicity
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Store settings as JSON
    settings = Column(JSON, default={
        "default_language": "python",
        "default_framework": "fastapi",
        "enable_ai_assistance": True,
        "enable_collaboration": True,
        "max_storage_gb": 100,
        "max_projects": 50
    })
    
    # Relationships
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    activities = relationship("WorkspaceActivity", back_populates="workspace", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workspace {self.name} (ID: {self.id})>"

class WorkspaceMember(Base):
    """Workspace Member association"""
    __tablename__ = "workspace_members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    username = Column(String)
    role = Column(String, nullable=False) # admin, enterprise, pro_developer, developer
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="members")

    def __repr__(self):
        return f"<WorkspaceMember {self.user_id} in {self.workspace_id}>"

class WorkspaceActivity(Base):
    """Workspace Activity Log"""
    __tablename__ = "workspace_activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    user_id = Column(String, nullable=True) # ID of user who performed action
    activity_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="activities")

    def __repr__(self):
        return f"<WorkspaceActivity {self.activity_type} in {self.workspace_id}>"
