"""
MCP Protocol Models
Based on Model Context Protocol specification
"""
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel

class JSONRPCMessage(BaseModel):
    jsonrpc: str = "2.0"

class JSONRPCRequest(JSONRPCMessage):
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None

class JSONRPCResponse(JSONRPCMessage):
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class ToolDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    inputSchema: Dict[str, Any]

class ListToolsResult(BaseModel):
    tools: List[ToolDefinition]

class CallToolRequest(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = None

class CallToolResult(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

class ServerCapabilities(BaseModel):
    tools: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    prompts: Optional[Dict[str, Any]] = None

class Implementation(BaseModel):
    name: str
    version: str

class InitializeParams(BaseModel):
    protocolVersion: str
    capabilities: Dict[str, Any]
    clientInfo: Implementation

class InitializeResult(BaseModel):
    protocolVersion: str
    capabilities: ServerCapabilities
    serverInfo: Implementation
