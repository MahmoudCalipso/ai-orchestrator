"""
Real-Time Monitoring Service
Provides build progress tracking, resource monitoring, and log streaming
"""
import asyncio
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import WebSocket
import json


class MonitoringMetrics:
    """Container for monitoring metrics"""
    
    def __init__(self):
        self.cpu_percent = 0.0
        self.memory_percent = 0.0
        self.memory_used_mb = 0
        self.disk_percent = 0.0
        self.disk_used_gb = 0.0
        self.network_sent_mb = 0.0
        self.network_recv_mb = 0.0
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "memory_used_mb": self.memory_used_mb,
            "disk_percent": self.disk_percent,
            "disk_used_gb": self.disk_used_gb,
            "network_sent_mb": self.network_sent_mb,
            "network_recv_mb": self.network_recv_mb,
            "timestamp": self.timestamp.isoformat()
        }


class BuildProgress:
    """Track build progress"""
    
    def __init__(self, build_id: str, project_name: str):
        self.build_id = build_id
        self.project_name = project_name
        self.status = "pending"  # pending, running, success, failed
        self.progress = 0.0  # 0-100
        self.current_step = ""
        self.total_steps = 0
        self.completed_steps = 0
        self.logs: List[str] = []
        self.errors: List[str] = []
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None
    
    def update(self, step: str, progress: float):
        """Update build progress"""
        self.current_step = step
        self.progress = min(100.0, max(0.0, progress))
        self.completed_steps += 1
    
    def add_log(self, message: str):
        """Add log message"""
        self.logs.append(f"[{datetime.utcnow().isoformat()}] {message}")
    
    def add_error(self, error: str):
        """Add error message"""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")
    
    def complete(self, success: bool):
        """Mark build as complete"""
        self.status = "success" if success else "failed"
        self.progress = 100.0
        self.end_time = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "build_id": self.build_id,
            "project_name": self.project_name,
            "status": self.status,
            "progress": self.progress,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "logs": self.logs[-100:],  # Last 100 logs
            "errors": self.errors,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time else None
        }


class RealtimeMonitoringService:
    """Real-time monitoring service"""
    
    def __init__(self):
        self.builds: Dict[str, BuildProgress] = {}
        self.websocket_connections: List[WebSocket] = []
        self.metrics_history: List[MonitoringMetrics] = []
        self.max_history = 1000
        self._monitoring_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start monitoring service"""
        if not self._monitoring_task:
            self._monitoring_task = asyncio.create_task(self._collect_metrics())
    
    async def stop(self):
        """Stop monitoring service"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
    
    async def _collect_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                metrics = MonitoringMetrics()
                
                # CPU metrics
                metrics.cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                metrics.memory_percent = memory.percent
                metrics.memory_used_mb = memory.used / (1024 * 1024)
                
                # Disk metrics
                disk = psutil.disk_usage('/')
                metrics.disk_percent = disk.percent
                metrics.disk_used_gb = disk.used / (1024 * 1024 * 1024)
                
                # Network metrics
                net_io = psutil.net_io_counters()
                metrics.network_sent_mb = net_io.bytes_sent / (1024 * 1024)
                metrics.network_recv_mb = net_io.bytes_recv / (1024 * 1024)
                
                # Store metrics
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Broadcast to connected clients
                await self._broadcast_metrics(metrics)
                
                await asyncio.sleep(5)  # Collect every 5 seconds
            except Exception as e:
                print(f"Error collecting metrics: {e}")
                await asyncio.sleep(5)
    
    async def _broadcast_metrics(self, metrics: MonitoringMetrics):
        """Broadcast metrics to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
        
        message = json.dumps({
            "type": "metrics",
            "data": metrics.to_dict()
        })
        
        disconnected = []
        for ws in self.websocket_connections:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            self.websocket_connections.remove(ws)
    
    async def register_websocket(self, websocket: WebSocket):
        """Register WebSocket connection"""
        self.websocket_connections.append(websocket)
    
    async def unregister_websocket(self, websocket: WebSocket):
        """Unregister WebSocket connection"""
        if websocket in self.websocket_connections:
            self.websocket_connections.remove(websocket)
    
    def create_build(self, build_id: str, project_name: str) -> BuildProgress:
        """Create new build tracking"""
        build = BuildProgress(build_id, project_name)
        self.builds[build_id] = build
        return build
    
    def get_build(self, build_id: str) -> Optional[BuildProgress]:
        """Get build progress"""
        return self.builds.get(build_id)
    
    def list_builds(self, status: Optional[str] = None) -> List[BuildProgress]:
        """List builds"""
        builds = list(self.builds.values())
        if status:
            builds = [b for b in builds if b.status == status]
        return sorted(builds, key=lambda x: x.start_time, reverse=True)
    
    async def stream_build_logs(self, build_id: str, websocket: WebSocket):
        """Stream build logs via WebSocket"""
        build = self.builds.get(build_id)
        if not build:
            await websocket.close(code=1008, reason="Build not found")
            return
        
        # Send existing logs
        for log in build.logs:
            await websocket.send_text(json.dumps({
                "type": "log",
                "message": log
            }))
        
        # Stream new logs
        last_log_count = len(build.logs)
        while build.status in ["pending", "running"]:
            await asyncio.sleep(0.5)
            
            # Send new logs
            if len(build.logs) > last_log_count:
                for log in build.logs[last_log_count:]:
                    await websocket.send_text(json.dumps({
                        "type": "log",
                        "message": log
                    }))
                last_log_count = len(build.logs)
            
            # Send progress update
            await websocket.send_text(json.dumps({
                "type": "progress",
                "data": build.to_dict()
            }))
        
        # Send final status
        await websocket.send_text(json.dumps({
            "type": "complete",
            "data": build.to_dict()
        }))
    
    def get_metrics(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent metrics"""
        return [m.to_dict() for m in self.metrics_history[-limit:]]
    
    def get_current_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics"""
        if self.metrics_history:
            return self.metrics_history[-1].to_dict()
        return None
