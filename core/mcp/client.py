"""
MCP Client Implementation
Handles communication with MCP Servers over stdio
"""
import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, List, Optional, Union
from core.mcp.protocol import (
    JSONRPCRequest, 
    JSONRPCResponse, 
    InitializeParams, 
    Implementation,
    ToolDefinition,
    CallToolResult
)

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for Model Context Protocol servers using stdio transport"""
    
    def __init__(self, name: str, command: str, args: List[str] = None):
        self.name = name
        self.command = command
        self.args = args or []
        self.process: Optional[asyncio.subprocess.Process] = None
        self.request_id = 0
        self.pending_requests: Dict[Union[str, int], asyncio.Future] = {}
        self.tools: List[ToolDefinition] = []
        self.capabilities: Dict[str, Any] = {}
        self._reader_task: Optional[asyncio.Task] = None

    async def connect(self):
        """Standard connect to the MCP server process"""
        logger.info(f"Connecting to MCP server '{self.name}' via {self.command} {' '.join(self.args)}")
        
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Start reader task
            self._reader_task = asyncio.create_task(self._read_loop())
            
            # Initialize connection
            await self._initialize()
            
            # Fetch tools
            await self.list_tools()
            
            logger.info(f"Connected to MCP server '{self.name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MCP server '{self.name}': {e}")
            return False

    async def _initialize(self):
        """Perform MCP handshake"""
        params = InitializeParams(
            protocolVersion="2024-11-05",
            capabilities={},
            clientInfo=Implementation(name="AI-Orchestrator-Client", version="1.0.0")
        )
        
        result = await self.send_request("initialize", params.model_dump())
        self.capabilities = result.get("capabilities", {})
        
        # Send initialized notification
        await self.send_notification("notifications/initialized", {})

    async def _read_loop(self):
        """Continuously read from server stdout"""
        try:
            while self.process and not self.process.stdout.at_eof():
                line = await self.process.stdout.readline()
                if not line:
                    break
                
                try:
                    message = json.loads(line.decode().strip())
                    await self._handle_message(message)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse MCP message: {line}")
                except Exception as e:
                    logger.error(f"Error handling MCP message: {e}")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"MCP client read loop error: {e}")

    async def _handle_message(self, message: Dict[str, Any]):
        """Handle incoming JSON-RPC message"""
        if "id" in message:
            # Response or Request (Client currently doesn't handle server-init requests yet)
            req_id = message["id"]
            if req_id in self.pending_requests:
                future = self.pending_requests.pop(req_id)
                if "error" in message:
                    future.set_exception(Exception(f"MCP Error: {message['error']}"))
                else:
                    future.set_result(message.get("result"))
        elif "method" in message:
            # Notification
            logger.debug(f"Received notification from {self.name}: {message['method']}")

    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Any:
        self.request_id += 1
        req_id = self.request_id
        
        request = JSONRPCRequest(id=req_id, method=method, params=params)
        
        future = asyncio.get_running_loop().create_future()
        self.pending_requests[req_id] = future
        
        await self._send(request.model_dump_json())
        
        return await future

    async def send_notification(self, method: str, params: Optional[Dict[str, Any]] = None):
        notification = {"jsonrpc": "2.0", "method": method, "params": params}
        await self._send(json.dumps(notification))

    async def _send(self, data: str):
        if not self.process or not self.process.stdin:
            raise RuntimeError("MCP Client is not connected")
        
        self.process.stdin.write((data + "\n").encode())
        await self.process.stdin.drain()

    async def list_tools(self) -> List[ToolDefinition]:
        """Fetch available tools from the server"""
        result = await self.send_request("tools/list")
        tools_data = result.get("tools", [])
        self.tools = [ToolDefinition(**t) for t in tools_data]
        return self.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Call a specific tool on the server"""
        result = await self.send_request("tools/call", {"name": name, "arguments": arguments})
        return CallToolResult(**result)

    async def disconnect(self):
        """Cleanly close connection"""
        if self._reader_task:
            self._reader_task.cancel()
        
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
        
        logger.info(f"Disconnected from MCP server '{self.name}'")

class MCPManager:
    """Manager for multiple MCP clients"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        
    async def register_server(self, name: str, command: str, args: List[str] = None):
        client = MCPClient(name, command, args)
        if await client.connect():
            self.clients[name] = client
            return True
        return False
        
    def get_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for client_name, client in self.clients.items():
            for tool in client.tools:
                all_tools.append({
                    "server": client_name,
                    "tool": tool.model_dump()
                })
        return all_tools

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]):
        if server_name not in self.clients:
            raise ValueError(f"MCP Server '{server_name}' not found")
        return await self.clients[server_name].call_tool(tool_name, arguments)
