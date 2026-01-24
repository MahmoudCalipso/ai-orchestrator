from typing import Optional
from pydantic import BaseModel, Field

class GitConfigUpdate(BaseModel):
    token: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    ssh_key: Optional[str] = None

class GitRepoInit(BaseModel):
    path: str = Field(..., description="Directory path to initialize")

class GitRemoteCreate(BaseModel):
    provider: str = Field(..., description="github or gitlab")
    name: str = Field(..., description="Repository name")
    description: str = ""
    private: bool = True

class GitBranchCreate(BaseModel):
    local_path: str
    branch_name: str
    base_branch: str = "main"

class GitCommitRequest(BaseModel):
    local_path: str
    message: str
    branch: str = "main"

class GitConflictResolve(BaseModel):
    local_path: str
    file_path: str

class GitMergeRequest(BaseModel):
    local_path: str
    source_branch: str
    target_branch: str = "main"
