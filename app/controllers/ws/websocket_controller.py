"""Robust WebSocket management with ConnectionPool and Heartbeats."""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages active WebSocket connections with heartbeats and locking."""
    
    def __init__(self):
        # Map of session_id -> set of active WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of session_id -> connection metadata
        self.connection_info: Dict[str, Dict] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accepts a connection and tracks it with strict resource limits."""
        async with self._lock:
            # V2.0 Requirement: Maximum 5 WebSockets per agent (prevent DoS/FD exhaustion)
            if session_id in self.active_connections and len(self.active_connections[session_id]) >= 5:
                await websocket.accept() # Must accept before closing gracefully
                await websocket.close(code=1008, reason="Max concurrent connections reached for agent")
                return

            await websocket.accept()
            if session_id not in self.active_connections:
                self.active_connections[session_id] = set()
            self.active_connections[session_id].add(websocket)
            self.connection_info[session_id] = {
                "connected_at": datetime.utcnow(),
                "last_heartbeat": datetime.utcnow()
            }
        logger.info(f"WebSocket connected: {session_id} (Connections: {len(self.active_connections[session_id])})")
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Removes a connection and cleans up session if empty."""
        async with self._lock:
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    if session_id in self.connection_info:
                        del self.connection_info[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Sends a JSON message to a specific websocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            # The connection will likely be cleaned up by the caller or heartbeat
    
    async def broadcast(self, message: dict, session_id: str):
        """Sends a JSON message to all clients in a session."""
        if session_id in self.active_connections:
            dead_connections = set()
            for connection in list(self.active_connections[session_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            if dead_connections:
                async with self._lock:
                    for dead_conn in dead_connections:
                        self.active_connections[session_id].discard(dead_conn)
    
    async def heartbeat_monitor(self):
        """Prunes stale connections and zombie sockets every 60s."""
        while True:
            await asyncio.sleep(60) # V2.0 Requirement: 60s ping/pong detection
            now = datetime.utcnow()
            async with self._lock:
                stale_sessions = []
                for session_id, info in self.connection_info.items():
                    # Close if no heartbeat for 60 seconds (Aggressive pruning)
                    if (now - info["last_heartbeat"]).total_seconds() > 60:
                        stale_sessions.append(session_id)
                
                for sid in stale_sessions:
                    logger.warning(f"Closing stale WebSocket session: {sid}")
                    for conn in list(self.active_connections.get(sid, [])):
                        try:
                            # V2.0 Requirement: code 1001 (going away)
                            await conn.close(code=1001)
                        except: pass
                    self.active_connections.pop(sid, None)
                    self.connection_info.pop(sid, None)

# Global connection manager instance
manager = ConnectionManager()
