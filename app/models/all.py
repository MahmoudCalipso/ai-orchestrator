""" 
Central Model Registry
Import all models here to ensure they are registered with SQLAlchemy Base.metadata
"""
# Infrastructure & Multi-Tenancy
from platform_core.tenancy.models import Tenant
from platform_core.auth.models import User, APIKey, RefreshToken, ExternalAccount, PasswordResetToken

# Core Agents
from app.models.agent import Agent

# Project Management & Solutions
from models.user_project import UserProject, ProjectSession, ProjectUpdate, WorkflowExecution
from models.solution import Solution
from models.workspace import Workspace, WorkspaceMember, WorkspaceActivity

# Engine & Intelligence
from core.database.models import NeuralMemory, UsageMetric
from platform_core.auth.audit_model import AuditLog

# Registry & Metadata
from services.registry.persistence import LanguageMetadata, DatabaseMetadata, FrameworkMetadata

# Registry & Metadata
# (Add any other models here as they are created)
