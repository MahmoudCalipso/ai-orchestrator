from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class GitCredentialsValidationDTO(BaseModel):
    valid: bool
    provider: str

class GitRepoInfoDTO(BaseModel):
    path: str

class GitBranchListResponseDTO(BaseModel):
    current_branch: Optional[str]
    branches: List[GitBranchDTO]

class GitCheckoutResponseDTO(BaseModel):
    branch: str

class GitBranchDTO(BaseModel):
    name: str = Field(..., description="Branch name")
    is_current: bool = Field(False, description="Whether this is the currently checked out branch")
    remote: Optional[str] = Field(None, description="Remote tracking branch if applicable")

class GitCommitDTO(BaseModel):
    hash: str = Field(..., description="Full commit SHA")
    short_hash: str = Field(..., description="Shortened commit SHA (7 chars)")
    author: str = Field(..., description="Commit author name")
    email: str = Field(..., description="Commit author email")
    date: str = Field(..., description="ISO 8601 commit timestamp")
    message: str = Field(..., description="Commit subject line")

class GitStatusResponseDTO(BaseModel):
    branch: str = Field(..., description="Current branch name")
    is_clean: bool = Field(..., description="True if there are no uncommitted changes")
    staged: List[str] = Field(default_factory=list, description="List of staged files")
    unstaged: List[str] = Field(default_factory=list, description="List of modified but unstaged files")
    untracked: List[str] = Field(default_factory=list, description="List of untracked files")
    ahead_behind: Optional[Dict[str, int]] = Field(None, description="Sync status with remote")

class GitLogResponseDTO(BaseModel):
    commits: List[GitCommitDTO] = Field(..., description="List of recent commits")
    total: int = Field(..., description="Total count of items in log (capped by limit)")

class GitActionResponseDTO(BaseModel):
    success: bool = Field(..., description="Whether the operation completed without errors")
    branch: str = Field(..., description="Target branch of the operation")
    output: str = Field(..., description="Raw command output or summary")
    error: Optional[str] = Field(None, description="Error message if success is False")
