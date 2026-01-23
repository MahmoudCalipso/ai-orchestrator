"""
CALTService - Cost and Latency Tracking
Atomic tracking for LLM calls, Tools (MCP), and Agent operations.
"""
import time
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class CALTLogger:
    """Atomic logger for tracking performance and financial metrics"""

    def __init__(self, log_dir: str = "storage/logs/calt"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.active_metrics: List[Dict[str, Any]] = []

    def log_operation(
        self, 
        operation_type: str, 
        duration: float, 
        tokens_in: int = 0, 
        tokens_out: int = 0, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an atomic operation with its performance and cost data"""
        
        # Estimate costs based on 2026 Open Source / Local serving averages (Simulated USD)
        # For local Ollama, cost is essentially 0, but we track "virtual cost" for billing simulation.
        virtual_cost = (tokens_in * 0.0001 + tokens_out * 0.0003) / 1000
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation_type,
            "duration_ms": int(duration * 1000),
            "tokens": {
                "in": tokens_in,
                "out": tokens_out,
                "total": tokens_in + tokens_out
            },
            "virtual_cost_usd": virtual_cost,
            "metadata": metadata or {}
        }
        
        self.active_metrics.append(entry)
        
        # Persist to disk (Daily log files)
        log_file = self.log_dir / f"calt_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        logger.info(f"CALT: {operation_type} | {entry['duration_ms']}ms | {entry['tokens']['total']} tokens | ${virtual_cost:.6f}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Aggregate metrics for the current session"""
        total_duration = sum(m["duration_ms"] for m in self.active_metrics)
        total_tokens = sum(m["tokens"]["total"] for m in self.active_metrics)
        total_cost = sum(m["virtual_cost_usd"] for m in self.active_metrics)
        
        return {
            "operation_count": len(self.active_metrics),
            "total_duration_ms": total_duration,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost,
            "avg_latency_ms": total_duration / len(self.active_metrics) if self.active_metrics else 0
        }
