import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from core.utils.subprocess import run_command_async

logger = logging.getLogger(__name__)

class BuildService:
    """Handles building projects asynchronously"""
    
    def __init__(self):
        pass
        
    async def build_project(
        self,
        local_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build a project asynchronously based on its language and configuration"""
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
            # 2. Run build command asynchronously
            code, stdout, stderr = await run_command_async(
                build_cmd,
                cwd=local_path,
                timeout=600  # 10 minutes
            )
            
            if code != 0:
                logger.error(f"Build failed: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "logs": stdout
                }
                
            return {
                "success": True,
                "logs": stdout,
                "message": "Build completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Build exception: {e}")
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
