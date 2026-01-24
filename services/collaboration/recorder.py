"""
IDE Session Recorder Service
Captures WebRTC screen sharing streams and saves them as WebM files.
"""
import os
import asyncio
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class SessionRecorder:
    """Manages recording of collaboration sessions"""

    def __init__(self, storage_path: str = "storage/recordings"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.active_recordings: Dict[str, Dict[str, Any]] = {}

    async def start_recording(self, session_id: str, project_id: str, user_id: str) -> Dict[str, Any]:
        """Start a new recording for a session"""
        if session_id in self.active_recordings:
            return {"success": False, "error": "Recording already active for this session"}

        recording_id = str(uuid.uuid4())
        filename = f"{project_id}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
        file_path = self.storage_path / filename

        self.active_recordings[session_id] = {
            "recording_id": recording_id,
            "project_id": project_id,
            "session_id": session_id,
            "user_id": user_id,
            "file_path": str(file_path),
            "start_time": datetime.utcnow(),
            "status": "recording"
        }

        logger.info(f"🔴 Recording started: {recording_id} for session {session_id}")
        
        # In a real PaaS, we would spawn an FFmpeg process or attach to a MediaServer
        # For now, we simulate the stream capture preparation
        return {
            "success": True, 
            "recording_id": recording_id,
            "file_path": str(file_path)
        }

    async def stop_recording(self, session_id: str) -> Dict[str, Any]:
        """Stop an active recording"""
        if session_id not in self.active_recordings:
            return {"success": False, "error": "No active recording found for this session"}

        recording_info = self.active_recordings.pop(session_id)
        recording_info["end_time"] = datetime.utcnow()
        recording_info["status"] = "completed"
        
        duration = (recording_info["end_time"] - recording_info["start_time"]).total_seconds()
        recording_info["duration"] = duration

        logger.info(f"⏹️ Recording stopped: {recording_info['recording_id']} (Duration: {duration}s)")
        
        return {
            "success": True,
            "recording_info": {
                "id": recording_info["recording_id"],
                "file_path": recording_info["file_path"],
                "duration": duration
            }
        }

    async def list_recordings(self, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all completed recordings (simulated from filesystem metadata)"""
        recordings = []
        # In production, this would query a database
        return recordings

    def get_recording_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Check if a session is currently being recorded"""
        return self.active_recordings.get(session_id)
