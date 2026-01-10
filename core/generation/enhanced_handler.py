"""
Enhanced Generation Request Handler
Processes generation requests with framework versions and best practices
"""
from typing import Dict, Any, List
from services.registry import framework_registry


class EnhancedGenerationHandler:
    """Handle enhanced generation requests with framework specifications"""
    
    def __init__(self):
        self.registry = framework_registry
    
    def process_language_spec(
        self,
        language_config: Dict[str, Any],
        database_type: str = None
    ) -> Dict[str, Any]:
        """Process language configuration and enrich with framework details"""
        result = {
            "backend": None,
            "frontend": None,
            "packages": {
                "backend": [],
                "frontend": []
            },
            "best_practices": {
                "backend": [],
                "frontend": []
            },
            "architecture_patterns": {
                "backend": [],
                "frontend": []
            }
        }
        
        # Process backend
        if "backend" in language_config and language_config["backend"]:
            backend_spec = language_config["backend"]
            
            if isinstance(backend_spec, dict):
                # New format with FrameworkSpec
                framework = backend_spec.get("framework")
                version = backend_spec.get("version")
                architecture = backend_spec.get("architecture")
                sdk = backend_spec.get("sdk")
                jdk = backend_spec.get("jdk")
                
                # Get language from framework
                language = self._get_language_from_framework(framework)
                
                # Get framework info
                framework_info = self.registry.get_framework_info(language, framework)
                
                if framework_info:
                    # Use specified version or get recommended
                    if not version:
                        version = framework_info.get("latest_version")
                    
                    # Get required packages
                    packages = self.registry.get_required_packages(
                        language,
                        framework,
                        database_type
                    )
                    
                    # Get best practices
                    best_practices = self.registry.get_best_practices(language, framework)
                    
                    # Get supported architectures
                    architectures = self.registry.get_supported_architectures(language, framework)
                    
                    # Validate architecture
                    if architecture and architecture not in architectures:
                        architecture = architectures[0] if architectures else "Layered"
                    
                    # Get SDK/JDK if not specified
                    if not sdk and "sdk_versions" in framework_info:
                        sdk = framework_info.get("recommended_sdk")
                    
                    if not jdk and "jdk_versions" in framework_info:
                        jdk = framework_info.get("recommended_jdk")
                    
                    result["backend"] = {
                        "language": language,
                        "framework": framework,
                        "version": version,
                        "architecture": architecture,
                        "sdk": sdk,
                        "jdk": jdk
                    }
                    result["packages"]["backend"] = packages
                    result["best_practices"]["backend"] = best_practices
                    result["architecture_patterns"]["backend"] = architectures
        
        # Process frontend
        if "frontend" in language_config and language_config["frontend"]:
            frontend_spec = language_config["frontend"]
            
            if isinstance(frontend_spec, dict):
                framework = frontend_spec.get("framework")
                version = frontend_spec.get("version")
                
                framework_info = self.registry.get_framework_info("frontend", framework)
                
                if framework_info:
                    if not version:
                        version = framework_info.get("latest_version")
                    
                    packages = self.registry.get_required_packages("frontend", framework)
                    best_practices = self.registry.get_best_practices("frontend", framework)
                    architectures = self.registry.get_supported_architectures("frontend", framework)
                    
                    result["frontend"] = {
                        "framework": framework,
                        "version": version
                    }
                    result["packages"]["frontend"] = packages
                    result["best_practices"]["frontend"] = best_practices
                    result["architecture_patterns"]["frontend"] = architectures
        
        return result
    
    def _get_language_from_framework(self, framework: str) -> str:
        """Map framework to language"""
        framework_map = {
            "django": "python",
            "fastapi": "python",
            "flask": "python",
            "express": "javascript",
            "nestjs": "javascript",
            "spring_boot": "java",
            "aspnet_core": "csharp",
            "gin": "go",
            "fiber": "go",
            "actix": "rust",
            "rocket": "rust"
        }
        return framework_map.get(framework.lower(), "python")
    
    def generate_package_install_script(
        self,
        language: str,
        packages: List[str]
    ) -> str:
        """Generate package installation script"""
        if language == "python":
            return f"pip install {' '.join(packages)}"
        elif language == "javascript":
            return f"npm install {' '.join(packages)}"
        elif language == "java":
            # Maven dependencies
            deps = "\n".join([
                f'<dependency>\n    <groupId>org.springframework.boot</groupId>\n    <artifactId>{pkg}</artifactId>\n</dependency>'
                for pkg in packages
            ])
            return deps
        elif language == "csharp":
            return "\n".join([f"dotnet add package {pkg}" for pkg in packages])
        elif language == "go":
            return "\n".join([f"go get {pkg}" for pkg in packages])
        
        return ""
    
    def generate_requirements_file(
        self,
        language: str,
        packages: List[str]
    ) -> str:
        """Generate requirements/package file content"""
        if language == "python":
            return "\n".join(packages)
        elif language == "javascript":
            # Generate package.json dependencies
            deps = {pkg: "latest" for pkg in packages}
            import json
            return json.dumps({"dependencies": deps}, indent=2)
        
        return ""
    
    def get_architecture_template(
        self,
        architecture: str,
        language: str
    ) -> Dict[str, Any]:
        """Get architecture-specific project structure"""
        templates = {
            "MVP": {
                "directories": ["models", "views", "presenters", "services"],
                "description": "Model-View-Presenter pattern"
            },
            "MVC": {
                "directories": ["models", "views", "controllers", "services"],
                "description": "Model-View-Controller pattern"
            },
            "Clean Architecture": {
                "directories": [
                    "domain/entities",
                    "domain/repositories",
                    "application/use_cases",
                    "application/interfaces",
                    "infrastructure/database",
                    "infrastructure/external",
                    "presentation/api",
                    "presentation/dto"
                ],
                "description": "Clean Architecture with clear layer separation"
            },
            "Hexagonal": {
                "directories": [
                    "core/domain",
                    "core/ports",
                    "adapters/primary/api",
                    "adapters/secondary/database",
                    "adapters/secondary/external"
                ],
                "description": "Hexagonal (Ports and Adapters) architecture"
            },
            "Repository Pattern": {
                "directories": [
                    "models",
                    "repositories",
                    "services",
                    "controllers",
                    "dto"
                ],
                "description": "Repository pattern for data access"
            }
        }
        
        return templates.get(architecture, templates["Repository Pattern"])
