"""
Kubernetes Manifest Generator
"""
import logging
import yaml
from typing import Dict, Any, List
from schemas.generation_spec import KubernetesConfig

logger = logging.getLogger(__name__)

class KubernetesGenerator:
    """Generates Kubernetes manifests"""
    
    def generate_manifests(self, app_name: str, image: str, config: KubernetesConfig) -> Dict[str, str]:
        """Generate standard K8s manifests"""
        
        manifests = {}
        
        # 1. Deployment
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": app_name,
                "namespace": config.namespace,
                "labels": {"app": app_name}
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {
                    "matchLabels": {"app": app_name}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": app_name}
                    },
                    "spec": {
                        "containers": [{
                            "name": app_name,
                            "image": image,
                            "ports": [{"containerPort": 8080}],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"}
                            }
                        }]
                    }
                }
            }
        }
        manifests["deployment.yaml"] = yaml.dump(deployment)
        
        # 2. Service
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": app_name,
                "namespace": config.namespace
            },
            "spec": {
                "selector": {"app": app_name},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 8080}],
                "type": "ClusterIP"
            }
        }
        manifests["service.yaml"] = yaml.dump(service)
        
        # 3. Ingress (if domain provided)
        if config.ingress_domain:
            ingress = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "Ingress",
                "metadata": {
                    "name": app_name,
                    "namespace": config.namespace,
                    "annotations": {
                        "kubernetes.io/ingress.class": "nginx"
                    }
                },
                "spec": {
                    "rules": [{
                        "host": config.ingress_domain,
                        "http": {
                            "paths": [{
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": app_name,
                                        "port": {"number": 80}
                                    }
                                }
                            }]
                        }
                    }]
                }
            }
            manifests["ingress.yaml"] = yaml.dump(ingress)
            
        return manifests

    def generate_helm_chart(self, app_name: str) -> Dict[str, str]:
        """Generate Helm chart foundation"""
        return {
            "Chart.yaml": yaml.dump({
                "apiVersion": "v2",
                "name": app_name,
                "description": f"Helm chart for {app_name}",
                "type": "application",
                "version": "0.1.0",
                "appVersion": "1.0.0"
            }),
            "values.yaml": yaml.dump({
                "replicaCount": 1,
                "image": {
                    "repository": app_name,
                    "pullPolicy": "IfNotPresent",
                    "tag": "latest"
                }
            })
        }
