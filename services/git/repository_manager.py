"""
Git Repository Manager
"""
import os
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any

from .credential_manager import GitCredentialManager

logger = logging.getLogger(__name__)

class RepositoryManager:
    """Manages Git repository operations"""
    
    def __init__(self, credential_manager: GitCredentialManager):
        self.credential_manager = credential_manager
        
    def init_repository(self, path: str, git_config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize a new local git repository"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                path_obj.mkdir(parents=True, exist_ok=True)
                
            # git init
            subprocess.run(["git", "init"], cwd=path, check=True)
            
            # Configure user for this repo
            config = git_config or self.credential_manager.get_git_config()
            user_config = config.get("user", {})
            
            if user_config.get("name"):
                subprocess.run(["git", "config", "user.name", user_config["name"]], cwd=path, check=True)
            if user_config.get("email"):
                subprocess.run(["git", "config", "user.email", user_config["email"]], cwd=path, check=True)
                
            logger.info(f"Initialized git repository at {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to init repository: {e}")
            return False

    def create_remote_repository(self, provider: str, name: str, description: str = "", private: bool = True) -> Optional[str]:
        """Create a remote repository on the provider"""
        # This would use provider-specific APIs (Github API, Gitlab API)
        # For this prototype, we'll assume it's implemented via API calls
        # Returns the clone URL
        
        creds = self.credential_manager.get_credentials(provider)
        if not creds:
             logger.error(f"No credentials for {provider}")
             return None
             
        # Placeholder logic
        logger.info(f"Mock: Creating remote repo {name} on {provider}")
        base_url = "https://github.com" if provider == "github" else "https://gitlab.com"
        owner = "ai-orchestrator-user" # Should come from creds/user info
        return f"{base_url}/{owner}/{name}.git"

    def push_to_remote(self, path: str, remote_url: str, branch: str = "main") -> bool:
         """Push local repo to remote"""
         try:
             # Add remote
             subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=path, check=True)
             
             # Add all files
             subprocess.run(["git", "add", "."], cwd=path, check=True)
             
             # Commit
             subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path, check=True)
             
             # Push (blindly assuming auth works via credential helper or SSH key for now)
             # In production, we'd inject credentials into the URL or use a custom helper
             subprocess.run(["git", "push", "-u", "origin", branch], cwd=path, check=True)
             
             logger.info(f"Pushed to {remote_url}")
             return True
         except Exception as e:
             logger.error(f"Failed to push to remote: {e}")
             return False
