from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EnterpriseUserResponseDTO(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str]
    is_active: bool
    created_at: Optional[str]

class WorkbenchMonitorDTO(BaseModel):
    id: str
    owner: str
    status: str
    last_active: Optional[str]

class EmulatorResponseDTO(BaseModel):
    id: str = Field(..., description="Active emulator session ID")
    device: str = Field(..., description="Device profile name")
    status: str = Field(..., description="Current lifecycle state (starting, running)")
    port: Optional[int] = Field(None, description="Local ADB port")

class IDEFileResponseDTO(BaseModel):
    path: str = Field(..., description="Absolute or relative file path")
    content: Optional[str] = Field(None, description="File text content (omit for large files)")
    size: int = Field(..., description="Size in bytes")
    encoding: str = Field("utf-8", description="Character encoding")

class IDETerminalResponseDTO(BaseModel):
    session_id: str = Field(..., description="Unique PTY session UUID")
    workspace_id: str

class IDETreeNodeDTO(BaseModel):
    name: str = Field(..., description="Display name of file or folder")
    path: str = Field(..., description="Relative path from workspace root")
    type: str = Field(..., description="file or directory")
    children: Optional[List['IDETreeNodeDTO']] = None

class AICompletionResponseDTO(BaseModel):
    completions: List[str] = Field(..., description="List of suggested code snippets")
    provider: str = Field("ollama", description="AI Backend provider")

class AIHoverResponseDTO(BaseModel):
    contents: str = Field(..., description="Markdown or plaintext documentation for the symbol")
    range: Optional[Dict[str, Any]] = None

class MetricSystemDTO(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, float]
    active_connections: int

class BuildSummaryDTO(BaseModel):
    id: str
    project_name: str
    status: str
    duration: float
    timestamp: str

class StorageStatsDTO(BaseModel):
    total_gb: float
    used_gb: float
    free_gb: float
    usage_percent: float
    project_count: int

class FigmaAnalysisResponseDTO(BaseModel):
    components_found: int
    layout_meta: Dict[str, Any]
    suggested_stack: str
    ui_preview_url: Optional[str] = None

class FrameworkDetailDTO(BaseModel):
    name: str
    versions: List[str]
    description: Optional[str] = None
    latest: str

class StoredProjectDTO(BaseModel):
    id: str
    project_name: str
    local_path: str
    status: str
    language: Optional[str] = None
    framework: Optional[str] = None
    size_mb: float = 0.0
    created_at: str
