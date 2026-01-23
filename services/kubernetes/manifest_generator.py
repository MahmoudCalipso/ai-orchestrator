"""
Kubernetes Manifest Generator
"""
import logging
import yaml
from typing import Dict
from schemas.generation_spec import KubernetesConfig

logger = logging.getLogger(__name__)

class KubernetesGenerator:
    """Generates Kubernetes manifests with AI-driven refinement"""
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator

    async def generate_manifests(self, app_name: str, image: str, config: Any) -> Dict[str, str]:
        """Generate and AI-refine K8s manifests"""
        
        # 1. Base generation (Legacy logic as foundation)
        manifests = self._generate_base_manifests(app_name, image, config)
        
        if not self.orchestrator:
            return manifests

        # 2. AI Refinement Pass
        logger.info(f"🚀 AI Power-Up: Refining Kubernetes manifests for '{app_name}'")
        task = f"Optimize and refine these Kubernetes manifests for production readiness: {app_name}"
        context = {
            "type": "k8s_optimization",
            "app_name": app_name,
            "image": image,
            "base_manifests": manifests,
            "requirements": "Ensure optimal resource allocation, security context best practices (non-root), and robust health checks."
        }

        try:
            result = await self.orchestrator.universal_agent.act(task, context)
            refined_solution = result.get("solution", "")
            
            # Extract refined YAMLs from AI response
            import re
            refined_manifests = {}
            yaml_blocks = re.findall(r'### File: (.*?)\n```(?:\w+)?\n(.*?)\n```', refined_solution, re.DOTALL)
            
            if yaml_blocks:
                for file_name, content in yaml_blocks:
                    refined_manifests[file_name.strip()] = content.strip()
                return refined_manifests
            
            return manifests # Fallback if AI didn't format correctly
        except Exception as e:
            logger.error(f"AI K8s refinement failed: {e}")
            return manifests

    def _generate_base_manifests(self, app_name: str, image: str, config: Any) -> Dict[str, str]:
        """Legacy generation logic used as starting point for AI"""
        manifests = {}
        
        # Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": app_name, "labels": {"app": app_name}},
            "spec": {
                "replicas": getattr(config, 'replicas', 1),
                "selector": {"matchLabels": {"app": app_name}},
                "template": {
                    "metadata": {"labels": {"app": app_name}},
                    "spec": {
                        "containers": [{
                            "name": app_name, "image": image,
                            "ports": [{"containerPort": 8080}]
                        }]
                    }
                }
            }
        }
        manifests["deployment.yaml"] = yaml.dump(deployment)
        
        # Service
        service = {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": app_name},
            "spec": {
                "selector": {"app": app_name},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 8080}],
                "type": "ClusterIP"
            }
        }
        manifests["service.yaml"] = yaml.dump(service)
        
        return manifests

    async def generate_helm_chart(self, app_name: str) -> Dict[str, str]:
        """AI-driven Helm chart generation"""
        if not self.orchestrator:
            return {"Chart.yaml": f"name: {app_name}", "values.yaml": "replicaCount: 1"}
            
        task = f"Generate a full production Helm chart for {app_name}"
        result = await self.orchestrator.universal_agent.act(task, {"type": "helm_generation"})
        # ... logic to parse files ...
        return {"result": result.get("solution")}
