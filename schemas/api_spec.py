"""
Comprehensive API Schemas for the AI Orchestrator
"""
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.generation_spec import LanguageConfig, EntityDefinition, GitActionConfig, DatabaseType

# --- AI Agent (Universal) Request Schemas ---

class CodeTaskRequest(BaseModel):
    """Base schema for simple code tasks"""
    code: str = Field(..., description="The source code to process")
    language: Optional[str] = Field(None, description="Programming language of the code")

class FixCodeRequest(CodeTaskRequest):
    """Request to fix code issues"""
    issue: str = Field(..., description="Description of the bug or issue to resolve")

class AnalyzeCodeRequest(CodeTaskRequest):
    """Request to analyze code"""
    analysis_type: str = Field("comprehensive", description="Type of analysis (security, performance, comprehensive)")

class TestCodeRequest(CodeTaskRequest):
    """Request to generate tests for code"""
    test_framework: Optional[str] = Field(None, description="Preferred test framework")

class OptimizeCodeRequest(CodeTaskRequest):
    """Request to optimize code"""
    optimization_goal: str = Field("performance", description="Goal of optimization (performance, memory, readability)")

class DocumentCodeRequest(CodeTaskRequest):
    """Request to generate documentation"""
    doc_style: str = Field("comprehensive", description="Style of documentation (comprehensive, api, user)")

class ReviewCodeRequest(CodeTaskRequest):
    """Request for code review"""
    pass

class ExplainCodeRequest(CodeTaskRequest):
    """Request to explain code"""
    pass

class RefactorCodeRequest(CodeTaskRequest):
    """Request to refactor code"""
    refactoring_goal: str = Field(..., description="Goal of the refactoring")

# --- Project-Level Schemas ---

class ProjectAnalyzeRequest(BaseModel):
    """Request to analyze a whole project"""
    project_path: str = Field(..., description="Local path to the project")

class ProjectAddFeatureRequest(BaseModel):
    """Request to add a feature to a project"""
    project_path: str = Field(..., description="Local path to the project")
    feature_description: str = Field(..., description="Description of the feature to add")

# --- Git Schemas ---

class GitConfigUpdate(BaseModel):
    """Request to update Git configuration"""
    token: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    ssh_key: Optional[str] = None

class GitRepoInit(BaseModel):
    """Request to initialize a Git repository"""
    path: str = Field(..., description="Directory path to initialize")

class GitRemoteCreate(BaseModel):
    """Request to create a remote repository"""
    provider: str = Field(..., description="github or gitlab")
    name: str = Field(..., description="Repository name")
    description: str = ""
    private: bool = True

class GitBranchCreate(BaseModel):
    """Request to create a branch"""
    local_path: str
    branch_name: str
    base_branch: str = "main"

class GitCommitRequest(BaseModel):
    """Request to commit changes"""
    local_path: str
    message: str
    branch: str = "main"

class GitConflictResolve(BaseModel):
    """Request to resolve a conflict via AI"""
    local_path: str
    file_path: str

class GitMergeRequest(BaseModel):
    """Request to merge branches"""
    local_path: str
    source_branch: str
    target_branch: str = "main"

# --- Workbench & Migration Schemas ---

class WorkbenchCreateRequest(BaseModel):
    """Request to create a workbench"""
    stack: str = Field(..., description="Flash stack name (e.g. react, nodejs, python)")
    project_name: str = Field(..., description="Name of the project")

class MigrationStartRequest(BaseModel):
    """Request to start a workbench-based migration"""
    source_stack: str
    target_stack: str
    project_path: Optional[str] = None

# --- Figma & Security Schemas ---

class FigmaAnalyzeRequest(BaseModel):
    """Request to analyze a Figma design"""
    file_key: str = Field(..., description="Figma file key")
    token: str = Field(..., description="Figma API token")

class SecurityScanRequest(BaseModel):
    """Request for a security scan"""
    project_path: str
    language: str = "python"
    type: str = "all"  # code, dependencies, all

# --- IDE Schemas ---

class IDEWorkspaceRequest(BaseModel):
    """Request to manage IDE workspace"""
    workspace_id: str

class IDEFileWriteRequest(BaseModel):
    """Request to write code to a file"""
    content: str

class IDETerminalRequest(BaseModel):
    """Request to create a terminal session"""
    workspace_id: str
    shell: str = "/bin/bash"

class IDEDebugRequest(BaseModel):
    """Request to create a debug session"""
    workspace_id: str
    language: str
    program: str
    args: List[str] = []

# --- Collaboration & Workspace Schemas ---

class CollaborationSessionRequest(BaseModel):
    """Request to create a collaboration session"""
    project_id: str
    owner_id: str
    owner_name: str

class WorkspaceCreateRequest(BaseModel):
    """Request to create a new user workspace"""
    name: str
    owner_id: str
    owner_name: str

class WorkspaceInviteRequest(BaseModel):
    """Request to invite a member to a workspace"""
    inviter_id: str
    user_id: str
    username: str
    role: str = "developer"

# --- Generic Response Schemas ---

class StandardResponse(BaseModel):
    """Legacy Standard API response"""
    status: str = "success"
    message: Optional[str] = None
    result: Optional[Any] = None

class PowerfulResponse(BaseModel):
    """The 'Magic' Response Schema for 2026+ Orchestrator"""
    status: str = Field("success", description="Status of the operation (success, error, warning)")
    code: int = Field(200, description="Internal or HTTP status code")
    message: str = Field("Operation completed successfully", description="Human-readable message")
    data: Optional[Any] = Field(None, description="The primary payload (result object or list)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Pagination, search info, or system telemetry")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO timestamp of the response")

class PowerfulError(BaseModel):
    """Structured Error details"""
    code: str
    detail: str
    field: Optional[str] = None

class PowerfulErrorResponse(PowerfulResponse):
    """Standardized Error response"""
    status: str = "error"
    code: int = 400
    message: str = "An error occurred"
    errors: Optional[List[PowerfulError]] = None

class SwarmResponse(BaseModel):
    """Response from a swarm-powered operation"""
    status: str = "success"
    type: str
    decomposition: Optional[List[Dict[str, Any]]] = None
    worker_results: Optional[Dict[str, Any]] = None
    migrated_files: Optional[Dict[str, str]] = None
    generated_files: Optional[Dict[str, str]] = None
    documentation: Optional[str] = None
    agent: Optional[str] = Field(None, description="The agent that handled the request")
