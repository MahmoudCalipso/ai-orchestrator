"""
Git Repository Manager
"""
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

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

    def create_ghost_branch(self, path: str, base_branch: str = "main") -> str:
        """Create a temporary 'ghost' branch for AI changes"""
        import time
        ghost_name = f"ai-ghost-{int(time.time())}"
        try:
            subprocess.run(["git", "checkout", "-b", ghost_name, base_branch], cwd=path, check=True)
            logger.info(f"Ghost branch {ghost_name} created from {base_branch}")
            return ghost_name
        except Exception as e:
            logger.error(f"Failed to create ghost branch: {e}")
            return base_branch

    def merge_ghost(self, path: str, ghost_branch: str, target_branch: str = "main"):
        """Merge ghost branch back with automatic conflict detection"""
        try:
            subprocess.run(["git", "checkout", target_branch], cwd=path, check=True)
            result = subprocess.run(["git", "merge", ghost_branch], cwd=path, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Merge conflict detected merging {ghost_branch} into {target_branch}")
                conflicts = self._get_conflicted_files(path)
                return {
                    "status": "conflict",
                    "conflicted_files": conflicts,
                    "message": "Automatic merge failed; manual or AI resolution required."
                }
            
            # Cleanup ghost branch after successful merge
            subprocess.run(["git", "branch", "-d", ghost_branch], cwd=path)
            return {"status": "success", "message": f"Successfully merged {ghost_branch}"}
        except Exception as e:
            logger.error(f"Merge error: {e}")
            return {"status": "error", "message": str(e)}

    def _get_conflicted_files(self, path: str) -> list:
        """Get list of files with merge conflicts"""
        try:
            result = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], cwd=path, capture_output=True, text=True)
            return result.stdout.splitlines()
        except:
            return []

    async def ai_resolve_conflict(self, path: str, file_path: str, orchestrator) -> bool:
        """Use AI to resolve a merge conflict in a specific file"""
        from pathlib import Path
        full_path = Path(path) / file_path
        if not full_path.exists(): return False
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
                
            if "<<<<<<<" not in content:
                return True # Already resolved?
                
            prompt = f"""
            Resolve the following git merge conflict in {file_path}.
            Choose the better implementation or merge them logically if possible.
            
            CONFLICTED CONTENT:
            {content}
            
            Respond only with the resolved file content, no explanations.
            """
            
            # Simple AI call via orchestrator
            result = await orchestrator.run_inference(prompt=prompt, task_type="fix")
            resolved_content = result.get("output", "")
            
            if resolved_content and "<<<<<<<" not in resolved_content:
                with open(full_path, 'w') as f:
                    f.write(resolved_content)
                subprocess.run(["git", "add", file_path], cwd=path, check=True)
                return True
                
            return False
        except Exception as e:
            logger.error(f"AI conflict resolution failed for {file_path}: {e}")
            return False
