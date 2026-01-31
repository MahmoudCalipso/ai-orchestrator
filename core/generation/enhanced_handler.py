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
        """Process language configuration and enrich with framework details using Registry intelligence"""
        result = {
            "backend": None,
            "frontend": None,
            "packages": {"backend": [], "frontend": []},
            "best_practices": {"backend": [], "frontend": []},
            "architecture_patterns": {"backend": [], "frontend": []}
        }
        
        # Process backend
        if "backend" in language_config and language_config["backend"]:
            spec = language_config["backend"]
            if isinstance(spec, dict):
                framework = spec.get("framework")
                version = spec.get("version")
                architecture = spec.get("architecture")
                
                # Use registry for all intelligence
                language = self.registry.get_framework_language(framework)
                framework_info = self.registry.get_framework_info(None, language, framework)
                
                if framework_info:
                    version = version or framework_info.get("latest_version")
                    packages = self.registry.get_required_packages(language, framework, database_type)
                    best_practices = self.registry.get_best_practices(language, framework)
                    architectures = self.registry.get_supported_architectures(language, framework)
                    
                    if architecture and architecture not in architectures:
                        architecture = architectures[0] if architectures else "Clean Architecture"
                    
                    result["backend"] = {
                        "language": language,
                        "framework": framework,
                        "version": version,
                        "architecture": architecture,
                        "sdk": spec.get("sdk") or framework_info.get("recommended_sdk"),
                        "jdk": spec.get("jdk") or framework_info.get("recommended_jdk")
                    }
                    result["packages"]["backend"] = packages
                    result["best_practices"]["backend"] = best_practices
                    result["architecture_patterns"]["backend"] = architectures
        
        # Process frontend
        if "frontend" in language_config and language_config["frontend"]:
            spec = language_config["frontend"]
            if isinstance(spec, dict):
                framework = spec.get("framework")
                version = spec.get("version")
                
                language = "typescript" # Core assumption for frontend in IA-ORCH
                framework_info = self.registry.get_framework_info("frontend", language, framework)
                
                if framework_info:
                    version = version or framework_info.get("latest_version")
                    packages = self.registry.get_required_packages(language, framework)
                    best_practices = self.registry.get_best_practices(language, framework)
                    architectures = self.registry.get_supported_architectures(language, framework)
                    
                    result["frontend"] = {
                        "language": language,
                        "framework": framework,
                        "version": version
                    }
                    result["packages"]["frontend"] = packages
                    result["best_practices"]["frontend"] = best_practices
                    result["architecture_patterns"]["frontend"] = architectures
        
        return result
    
    def generate_package_install_script(
        self,
        language: str,
        packages: List[str]
    ) -> str:
        """Generate package installation script based on language standards"""
        lang = language.lower()
        if lang == "python":
            return f"pip install {' '.join(packages)}"
        elif lang in ["javascript", "typescript"]:
            return f"npm install {' '.join(packages)}"
        elif lang == "java":
            return "\n".join([f"mvn install:install-file -DartifactId={pkg}" for pkg in packages])
        elif lang == "csharp":
            return "\n".join([f"dotnet add package {pkg}" for pkg in packages])
        elif lang == "go":
            return "\n".join([f"go get {pkg}" for pkg in packages])
        return ""
    
    def generate_requirements_file(
        self,
        language: str,
        packages: List[str]
    ) -> str:
        """Generate requirements/package file content"""
        lang = language.lower()
        if lang == "python":
            return "\n".join(packages)
        elif lang in ["javascript", "typescript"]:
            import json
            return json.dumps({"dependencies": {pkg: "latest" for pkg in packages}}, indent=2)
        return ""
    
    def get_architecture_template(
        self,
        architecture: str,
        language: str,
        framework: str = None
    ) -> Dict[str, Any]:
        """Get project structure from Registry intelligence"""
        return self.registry.get_architecture_template(architecture, language, framework)
