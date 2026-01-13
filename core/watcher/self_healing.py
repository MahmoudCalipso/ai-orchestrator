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
        URGENT: CRITICAL SYSTEM ERROR detected in {context_name}.
        Error Line: {error_line}
        
        SWARM CHALLENGE:
        1. AUDIT: Analyze the logs and project context.
        2. FIX: Generate a permanent fix that adheres to 2026 security standards.
        3. VERIFY: Ensure NO side effects.
        """
        
        logger.info("Self-Healing: Orchestrating swarm for elite autonomous repair...")
        
        import asyncio
        asyncio.create_task(
            self.orchestrator.run_inference(
                prompt=repair_task, 
                task_type="self_healing",
                context={"type": "self_healing", "priority": "critical", "source": context_name}
            )
        )

    def register_pattern(self, pattern: str):
        """Add custom error patterns to watch for"""
        self.error_patterns.append(pattern)
