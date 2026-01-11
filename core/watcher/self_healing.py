"""
Self-Healing Service - Proactive Error Repair
Watches terminal/logs and triggers LeadArchitect for autonomous fixing
"""
import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class SelfHealingService:
    """Service that monitors system health and triggers autonomous repairs"""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.active_watches: List[str] = []
        self.error_patterns = [
            r"Error:.*",
            r"Exception:.*",
            r"failed with exit code \d+",
            r"SyntaxError:.*",
            r"ModuleNotFoundError:.*"
        ]

    async def monitor_output(self, stream_name: str, line: str):
        """Analyze a single line of output for errors"""
        for pattern in self.error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                logger.warning(f"Self-Healing: Error detected in {stream_name}: {line.strip()}")
                await self._trigger_repair(stream_name, line)

    async def _trigger_repair(self, context_name: str, error_line: str):
        """Invoke the Lead Architect to fix the detected error"""
        repair_task = f"""
        URGENT: A runtime error was detected in {context_name}.
        Error details: {error_line}
        
        Please analyze the logs, identify the root cause, and propose a fix.
        """
        
        logger.info("Self-Healing: Triggering Lead Architect for autonomous repair...")
        
        # We run this as a background task to not block the main stream
        import asyncio
        asyncio.create_task(
            self.orchestrator.lead_architect.act(repair_task, {"type": "self_healing", "priority": "high"})
        )

    def register_pattern(self, pattern: str):
        """Add custom error patterns to watch for"""
        self.error_patterns.append(pattern)
