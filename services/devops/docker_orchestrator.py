"""
Docker Orchestrator Service
Generates stack-specific Docker configurations and multi-container orchestration
"""
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DockerOrchestrator:
    """Generates Docker and Docker Compose configurations for multi-stack projects"""
    
    def __init__(self):
        self.stack_templates = {
            "fastapi": {
                "dockerfile": """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
            },
            "react": {
                "dockerfile": """FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""
            },
            "nestjs": {
                "dockerfile": """FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start:prod"]
"""
            }
            # Add more templates as needed
        }

    def generate_dockerfile(self, stack: str, custom_requirements: Optional[str] = None) -> str:
        """Generate a Dockerfile for a specific stack"""
        template = self.stack_templates.get(stack.lower())
        if template:
            return template["dockerfile"]
        
        # Fallback generic Dockerfile
        return f"""FROM alpine:latest
# Placeholder for {stack}
WORKDIR /app
COPY . .
CMD ["echo", "Running {stack}"]
"""

    def generate_compose(self, services: List[Dict[str, Any]], database_type: str = "postgresql") -> str:
        """Generate a docker-compose.yml for the entire stack"""
        compose = {
            "version": "3.8",
            "services": {}
        }
        
        # Add database service
        db_service_name = "database"
        if database_type == "postgresql":
            compose["services"][db_service_name] = {
                "image": "postgres:16-alpine",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                    "POSTGRES_DB=app_db"
                ],
                "ports": ["5432:5432"],
                "volumes": ["db_data:/var/lib/postgresql/data"]
            }
        elif database_type == "mongodb":
            compose["services"][db_service_name] = {
                "image": "mongo:7.0",
                "ports": ["27017:27017"],
                "volumes": ["db_data:/data/db"]
            }
        
        # Add application services
        for svc in services:
            name = svc.get("name", "app").lower()
            stack = svc.get("stack", "general")
            port = svc.get("port", 8080)
            
            compose["services"][name] = {
                "build": {
                    "context": f"./{name}",
                    "dockerfile": "Dockerfile"
                },
                "ports": [f"{port}:{port}"],
                "depends_on": [db_service_name],
                "environment": [
                    f"DATABASE_URL={database_type}://user:password@database:5432/app_db"
                ]
            }
            
        compose["volumes"] = {"db_data": {}}
        
        # Convert to YAML-like string (very basic implementation)
        import yaml
        return yaml.dump(compose, sort_keys=False)

docker_orchestrator = DockerOrchestrator()
