"""
WebRTC Collaboration Service
Provides screen sharing, collaborative editing, and real-time chat
"""
import json
from typing import Dict, Any, List, Optional
from fastapi import WebSocket
from datetime import datetime
import uuid


class CollaborationSession:
    """Represents a collaboration session"""
    
    def __init__(self, session_id: str, project_id: str, owner_id: str):
        self.session_id = session_id
        self.project_id = project_id
        self.owner_id = owner_id
        self.participants: Dict[str, Dict[str, Any]] = {}
        self.created_at = datetime.utcnow()
        self.active = True
        self.screen_sharing_user: Optional[str] = None
    
    def add_participant(self, user_id: str, username: str, websocket: WebSocket):
        """Add participant to session"""
        self.participants[user_id] = {
            "user_id": user_id,
            "username": username,
            "websocket": websocket,
            "joined_at": datetime.utcnow(),
            "cursor_position": None,
            "is_typing": False
        }
    
    def remove_participant(self, user_id: str):
        """Remove participant from session"""
        if user_id in self.participants:
            del self.participants[user_id]
            if user_id == self.screen_sharing_user:
                self.screen_sharing_user = None
    
    def get_participant_list(self) -> List[Dict[str, Any]]:
        """Get list of participants"""
        return [
            {
                "user_id": p["user_id"],
                "username": p["username"],
                "joined_at": p["joined_at"].isoformat(),
                "is_screen_sharing": p["user_id"] == self.screen_sharing_user
            }
            for p in self.participants.values()
        ]
    
    async def broadcast(self, message: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast message to all participants"""
        disconnected = []
        for user_id, participant in self.participants.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await participant["websocket"].send_text(json.dumps(message))
            except Exception:
                disconnected.append(user_id)
        
        # Remove disconnected participants
        for user_id in disconnected:
            self.remove_participant(user_id)


class WebRTCSignalingService:
    """WebRTC signaling service for peer-to-peer connections"""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
    
    async def create_session(
        self,
        project_id: str,
        owner_id: str,
        owner_name: str
    ) -> str:
        """Create collaboration session"""
        session_id = str(uuid.uuid4())
        session = CollaborationSession(session_id, project_id, owner_id)
        self.sessions[session_id] = session
        return session_id
    
    async def join_session(
        self,
        session_id: str,
        user_id: str,
        username: str,
        websocket: WebSocket
    ) -> bool:
        """Join collaboration session"""
        session = self.sessions.get(session_id)
        if not session or not session.active:
            return False
        
        session.add_participant(user_id, username, websocket)
        
        # Notify other participants
        await session.broadcast({
            "type": "participant_joined",
            "user_id": user_id,
            "username": username,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
        
        # Send current participants to new user
        await websocket.send_text(json.dumps({
            "type": "participants_list",
            "participants": session.get_participant_list()
        }))
        
        return True
    
    async def leave_session(self, session_id: str, user_id: str):
        """Leave collaboration session"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        session.remove_participant(user_id)
        
        # Notify other participants
        await session.broadcast({
            "type": "participant_left",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Close session if no participants
        if not session.participants:
            session.active = False
    
    async def handle_webrtc_signal(
        self,
        session_id: str,
        from_user: str,
        to_user: str,
        signal: Dict[str, Any]
    ):
        """Handle WebRTC signaling (offer, answer, ICE candidates)"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        to_participant = session.participants.get(to_user)
        if not to_participant:
            return
        
        # Forward signal to target user
        await to_participant["websocket"].send_text(json.dumps({
            "type": "webrtc_signal",
            "from_user": from_user,
            "signal": signal
        }))
    
    async def start_screen_sharing(self, session_id: str, user_id: str) -> bool:
        """Start screen sharing"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Only one user can share screen at a time
        if session.screen_sharing_user and session.screen_sharing_user != user_id:
            return False
        
        session.screen_sharing_user = user_id
        
        # Notify all participants
        await session.broadcast({
            "type": "screen_sharing_started",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return True
    
    async def stop_screen_sharing(self, session_id: str, user_id: str):
        """Stop screen sharing"""
        session = self.sessions.get(session_id)
        if not session or session.screen_sharing_user != user_id:
            return
        
        session.screen_sharing_user = None
        
        # Notify all participants
        await session.broadcast({
            "type": "screen_sharing_stopped",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })


class CollaborativeEditingService:
    """Collaborative editing service using CRDT"""
    
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.cursors: Dict[str, Dict[str, Any]] = {}
    
    async def update_cursor(
        self,
        session_id: str,
        user_id: str,
        file_path: str,
        line: int,
        column: int
    ):
        """Update user cursor position"""
        key = f"{session_id}:{file_path}"
        
        if key not in self.cursors:
            self.cursors[key] = {}
        
        self.cursors[key][user_id] = {
            "line": line,
            "column": column,
            "timestamp": datetime.utcnow()
        }
    
    async def get_cursors(self, session_id: str, file_path: str) -> Dict[str, Any]:
        """Get all cursor positions for file"""
        key = f"{session_id}:{file_path}"
        return self.cursors.get(key, {})
    
    async def apply_edit(
        self,
        session_id: str,
        user_id: str,
        file_path: str,
        edit: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply collaborative edit (would use CRDT in production)"""
        # This is a simplified version
        # In production, use Yjs or Automerge for CRDT
        
        return {
            "success": True,
            "edit_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }


class ChatService:
    """Real-time chat service"""
    
    def __init__(self):
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
    
    async def send_message(
        self,
        session_id: str,
        user_id: str,
        username: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send chat message"""
        if session_id not in self.messages:
            self.messages[session_id] = []
        
        msg = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "username": username,
            "message": message,
            "type": message_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.messages[session_id].append(msg)
        
        # Keep only last 1000 messages
        if len(self.messages[session_id]) > 1000:
            self.messages[session_id] = self.messages[session_id][-1000:]
        
        return msg
    
    async def get_messages(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get chat messages"""
        messages = self.messages.get(session_id, [])
        return messages[-limit:]
    
    async def share_code_snippet(
        self,
        session_id: str,
        user_id: str,
        username: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Share code snippet in chat"""
        return await self.send_message(
            session_id,
            user_id,
            username,
            json.dumps({"code": code, "language": language}),
            message_type="code_snippet"
        )


class CollaborationService:
    """Main collaboration service"""
    
    def __init__(self):
        self.webrtc = WebRTCSignalingService()
        self.editing = CollaborativeEditingService()
        self.chat = ChatService()
    
    async def create_session(self, project_id: str, owner_id: str, owner_name: str) -> str:
        """Create collaboration session"""
        return await self.webrtc.create_session(project_id, owner_id, owner_name)
    
    async def handle_websocket(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str,
        username: str
    ):
        """Handle WebSocket connection for collaboration"""
        # Join session
        joined = await self.webrtc.join_session(session_id, user_id, username, websocket)
        if not joined:
            await websocket.close(code=1008, reason="Session not found")
            return
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await self._handle_message(session_id, user_id, username, message, websocket)
        except Exception as e:
            print(f"Collaboration WebSocket error: {e}")
        finally:
            await self.webrtc.leave_session(session_id, user_id)
    
    async def _handle_message(
        self,
        session_id: str,
        user_id: str,
        username: str,
        message: Dict[str, Any],
        websocket: WebSocket
    ):
        """Handle incoming WebSocket message"""
        msg_type = message.get("type")
        
        if msg_type == "webrtc_signal":
            await self.webrtc.handle_webrtc_signal(
                session_id,
                user_id,
                message.get("to_user"),
                message.get("signal")
            )
        
        elif msg_type == "start_screen_sharing":
            success = await self.webrtc.start_screen_sharing(session_id, user_id)
            await websocket.send_text(json.dumps({
                "type": "screen_sharing_response",
                "success": success
            }))
        
        elif msg_type == "stop_screen_sharing":
            await self.webrtc.stop_screen_sharing(session_id, user_id)
        
        elif msg_type == "cursor_update":
            await self.editing.update_cursor(
                session_id,
                user_id,
                message.get("file_path"),
                message.get("line"),
                message.get("column")
            )
            
            # Broadcast cursor position
            session = self.webrtc.sessions.get(session_id)
            if session:
                await session.broadcast({
                    "type": "cursor_update",
                    "user_id": user_id,
                    "file_path": message.get("file_path"),
                    "line": message.get("line"),
                    "column": message.get("column")
                }, exclude_user=user_id)
        
        elif msg_type == "chat_message":
            msg = await self.chat.send_message(
                session_id,
                user_id,
                username,
                message.get("message")
            )
            
            # Broadcast chat message
            session = self.webrtc.sessions.get(session_id)
            if session:
                await session.broadcast({
                    "type": "chat_message",
                    "message": msg
                })
