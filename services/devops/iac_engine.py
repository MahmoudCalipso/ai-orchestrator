"""
Autonomous IaC Engine
Generates professional Infrastructure as Code (Terraform, Kubernetes, Pulumi)
based on project architecture and framework metadata.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AutonomousIaCEngine:
    """Automates the generation of production-ready infrastructure code"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    async def generate_infrastructure(self, project_path: str, stack_info: Dict[str, Any], provider: str = "aws") -> Dict[str, str]:
        """Generate IaC files for a specific project and cloud provider"""
        logger.info(f"🚀 Extreme Power-Up: Generating Autonomous IaC for {provider} provider")
        
        # 1. Analyze stack and requirements
        base_stack = stack_info.get("language", "node")
        framework = stack_info.get("framework", "express")
        
        prompt = f"""
        YOU ARE THE CLOUD ARCHITECT AGENT.
        GENERATE PRODUCTION-READY INFRASTRUCTURE AS CODE for the following project:
        PROJECT PATH: {project_path}
        TECH STACK: {base_stack} / {framework}
        CLOUD PROVIDER: {provider}
        
        REQUIREMENTS:
        1. Multi-AZ High Availability.
        2. Auto-scaling groups or K8s Horizontal Pod Autoscalers.
        3. Automated SSL/TLS and WAF protection.
        4. Structured logging (OTel) and monitoring (Prometheus/Grafana) integration.
        5. Use Terraform for base infra and Kubernetes (Helm) for app deployment.
        
        Respond ONLY with a list of files in this exact format:
        FILE: path/to/file.ext
        ```
        CODE
        ```
        """
        
        context = {
            "type": "iac_generation",
            "provider": provider,
            "project_path": project_path,
            "stack_info": stack_info,
            "custom_prompt": prompt
        }

        try:
            # Use Universal Agent for IaC expertise
            result = await self.orchestrator.universal_agent.act("Generate complete IaC suite", context)
            solution = result.get("solution", "")
            
            import re
            file_blocks = re.findall(r'FILE:\s*(.*?)\n```(?:\w+)?\n(.*?)\n```', solution, re.DOTALL)
            
            files = {}
            if not file_blocks:
                logger.warning("Cloud Architect suggested IaC but no valid file blocks were extracted.")
                return {"error": "No IaC files generated"}

            for rel_path, content in file_blocks:
                # Save to a dedicated 'infra/' folder in the project
                infra_path = Path(project_path) / "infra" / rel_path.strip()
                infra_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(infra_path, "w", encoding="utf-8") as f:
                    f.write(content.strip())
                
                files[rel_path.strip()] = str(infra_path)
                logger.info(f"IaC Manifest Generated: {rel_path}")

            return files

        except Exception as e:
            logger.error(f"IaC Generation failed: {e}")
            return {"error": str(e)}

    def get_supported_providers(self) -> List[str]:
        return ["aws", "azure", "gcp", "kubernetes"]
