"""
__init__.py for core.mcp package
"""
from .client import MCPClient, MCPManager
from .protocol import (
    ToolDefinition,
    CallToolResult,
    InitializeResult,
    ServerCapabilities
)

__all__ = [
    'MCPClient',
    'MCPManager',
    'ToolDefinition',
    'CallToolResult',
    'InitializeResult',
    'ServerCapabilities'
]
