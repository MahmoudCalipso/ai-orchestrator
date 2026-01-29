from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class EmulatorStartRequest(BaseModel):
    project_id: str = Field(..., description="Unique ID of the project to associate with the emulator")
    device_profile: str = Field("Pixel_7_Pro", description="Name of the AVD/Device profile to launch")

class EmulatorStopRequest(BaseModel):
    emulator_id: str = Field(..., description="Active session ID or PID of the emulator to terminate")

class IDEFileWriteRequest(BaseModel):
    content: str = Field(..., description="Full text content to overwrite the file with")

class IDEDebugRequest(BaseModel):
    workspace_id: str = Field(..., description="Target IDE workspace ID")
    language: str = Field(..., description="Language debugger (python, node, go)")
    program: str = Field(..., description="Entry point file path")
    args: List[str] = Field(default_factory=list, description="CLI arguments for the debugger")
