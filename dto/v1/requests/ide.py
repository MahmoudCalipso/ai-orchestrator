from typing import List, Optional
from pydantic import BaseModel, Field

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
    args: List[str] = Field(default_factory=list)
