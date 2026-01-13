"""
Language and Framework Registry Manager
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class LanguageRegistry:
    """Manages language and framework configurations"""
    
    def __init__(self, registry_path: str = "services/registry/registries"):
        self.registry_path = Path(registry_path)
        self.registries: Dict[str, Any] = {}
        
    def load_registries(self):
        """Load all registry configurations"""
        if not self.registry_path.exists():
            logger.warning(f"Registry path {self.registry_path} does not exist")
            return
            
        for file in self.registry_path.glob("*_registry.json"):
            try:
                with open(file, 'r') as f:
                    config = json.load(f)
                    name = file.stem.replace("_registry", "")
                    self.registries[name] = config
                    logger.info(f"Loaded registry for {name}")
            except Exception as e:
                logger.error(f"Failed to load registry {file}: {e}")

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.registries.keys())

    def get_language_config(self, language: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific language"""
        return self.registries.get(language.lower())

    def validate_dependency(self, language: str, package: str, version: str) -> bool:
        """Validate if a dependency version is supported"""
        config = self.registries.get(language.lower())
        if not config:
            return False
            
        # Simplistic check - check if package exists in recommended packages
        # In a real implementation this would check npm/pypi/nuget
        packages = config.get("packages", {})
        if package in packages:
             # Logic to check version compatibility could go here
             return True
        return False
        
    def get_frameworks(self, language: str) -> List[Dict[str, Any]]:
        """Get supported frameworks for a language"""
        config = self.registries.get(language.lower())
        if not config:
            return []
        return config.get("frameworks", [])

    def get_latest_version(self, language: str) -> str:
        """Get latest stable version of a language"""
        config = self.registries.get(language.lower())
        if not config:
            return "unknown"
        return config.get("latest_version", "unknown")
