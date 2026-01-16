"""
Build Service
Handles project building using language-specific tools and Docker
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class BuildService:
    """Handles building projects"""
    
    def __init__(self):
        pass
        
    async def build_project(
        self,
        local_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a project based on its language and configuration"""
        local_path_obj = Path(local_path)
        logger.info(f"Building project at {local_path}")
        
        # 1. Detect language / build system
        build_info = self._detect_build_system(local_path_obj)
        
        if not build_info:
            return {
                "success": False, 
                "error": "Could not detect build system automatically. Please provide a build configuration."
            }
            
        build_cmd = build_info["command"]
        logger.info(f"Detected build system: {build_info['type']}. Running: {' '.join(build_cmd)}")
        
        try:
            # 2. Run build command
            result = subprocess.run(
                build_cmd,
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=600 # 10 minutes
            )
            
            if result.returncode != 0:
                logger.error(f"Build failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "logs": result.stdout
                }
                
            return {
                "success": True,
                "logs": result.stdout,
                "message": "Build completed successfully"
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _detect_build_system(self, path: Path) -> Optional[Dict[str, Any]]:
        """Detect the build system of a project"""
        if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
            return {"type": "python", "command": ["pip", "install", "-r", "requirements.txt"]}
        elif (path / "package.json").exists():
            return {"type": "nodejs", "command": ["npm", "install"]}
        elif (path / "pom.xml").exists():
            return {"type": "maven", "command": ["mvn", "clean", "install"]}
        elif (path / "build.gradle").exists():
            return {"type": "gradle", "command": ["gradle", "build"]}
        elif (path / "go.mod").exists():
            return {"type": "go", "command": ["go", "build", "./..."]}
        elif any(path.glob("*.sln")) or any(path.glob("*.csproj")):
            return {"type": "dotnet", "command": ["dotnet", "build"]}
        elif (path / "Dockerfile").exists():
            return {"type": "docker", "command": ["docker", "build", "-t", "project-build", "."]}
            
        return None
