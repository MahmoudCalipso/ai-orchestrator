"""
Migration Audit Agent - The "Code Surgeon"
Detects bugs, debt, and security issues in legacy codebases before migration.
"""
import logging
from typing import Dict, Any, List
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

class MigrationAuditAgent(BaseAgent):
    """Specialized agent for pre-migration source auditing"""
    
    def __init__(self, orchestrator=None):
        super().__init__(
            name="MigrationAudit",
            role="Code Forensic Specialist",
            system_prompt="""You are a Migration Audit Agent.
            Your mission is to perform a deep forensic analysis of legacy codebases.
            Identify:
            1. Logical bugs and runtime errors.
            2. Security vulnerabilities (OWASP Top 10).
            3. Architectural debt and anti-patterns (God objects, Spaghetti code).
            4. Redundant/Dead code.
            Produce an Audit Report that will guide the Migration Swarm to 'heal' the code.
            """
        )
        self.orchestrator = orchestrator

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """BaseAgent compliance - calls audit_project"""
        project_path = context.get("project_path")
        if not project_path:
            return {"error": "No project_path provided"}
        return await self.audit_project(project_path, context)

    async def audit_project(self, project_path: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform full project audit"""
        logger.info(f"Auditing project at {project_path} for migration...")
        
        # 1. Use Semantic RAG to find 'bad' areas if VectorStore is available
        audit_findings = []
        
        # 2. Heuristic/AI Audit Pass
        # We ask the LLM to analyze the project structure and key files
        # (Assuming the orchestrator has already indexed the files during the Scan phase)
        
        prompt = f"""
        Perform a high-level audit of the project at {project_path}.
        Based on the available context, locate the most critical issues to fix during migration.
        Focus on:
        - Outdated dependencies and their risks.
        - Complex logic that should be refactored.
        - Security flaws in auth/data handling.
        
        Provide a JSON list of 'findings' with keys: [type, location, severity, description, healing_instruction].
        """
        
        # Simple AI call via orchestrator
        # We assume the orchestrator uses RAG behind the scenes for this call
        response = await self.orchestrator.run_inference(prompt=prompt, task_type="analyze")
        
        return {
            "status": "success",
            "findings": response.get("output", []),
            "summary": "Source codebase audited. Ready for healing-based migration."
        }
