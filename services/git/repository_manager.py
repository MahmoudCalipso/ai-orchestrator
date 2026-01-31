import logging
import httpx
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .credential_manager import GitCredentialManager
from core.utils.subprocess import run_command_async
from core.utils.resilience import retry

logger = logging.getLogger(__name__)

class RepositoryManager:
    """Manages Git repository operations asynchronously"""
    
    def __init__(self, credential_manager: GitCredentialManager):
        self.credential_manager = credential_manager
        
    async def init_repository(self, path: str, git_config: Optional[Dict[str, Any]] = None) -> bool:
        """Initialize a new local git repository asynchronously"""
        try:
            path_obj = Path(path)
            path_obj.mkdir(parents=True, exist_ok=True)
                
            # git init
            code, stdout, stderr = await run_command_async(["git", "init"], cwd=path)
            if code != 0:
                logger.error(f"Failed to init repository: {stderr}")
                return False
            
            # Configure user for this repo
            config = git_config or self.credential_manager.get_git_config()
            user_config = config.get("user", {})
            
            if user_config.get("name"):
                await run_command_async(["git", "config", "user.name", user_config["name"]], cwd=path)
            if user_config.get("email"):
                await run_command_async(["git", "config", "user.email", user_config["email"]], cwd=path)
                
            logger.info(f"Initialized git repository at {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to init repository: {e}")
            return False

    async def create_remote_repository(self, provider: str, name: str, description: str = "", private: bool = True) -> Optional[str]:
        """Create a remote repository on the provider via API (Async)"""
        creds = self.credential_manager.get_credentials(provider)
        if not creds:
             logger.error(f"No credentials for {provider}")
             return None
             
        token = creds.get("token")
        if provider == "github":
            return await self._create_github_repo(name, description, private, token)
        elif provider == "gitlab":
            return await self._create_gitlab_repo(name, description, private, token)
            
        return None

    @retry(retries=3, delay=2.0)
    async def _create_github_repo(self, name: str, description: str, private: bool, token: str) -> Optional[str]:
        """Create repository via GitHub API"""
        url = "https://api.github.com/user/repos"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 201:
                repo_info = response.json()
                logger.info(f"GitHub repository created: {repo_info['html_url']}")
                return repo_info["clone_url"]
            else:
                logger.error(f"GitHub repo creation failed: {response.text}")
                return None

    @retry(retries=3, delay=2.0)
    async def _create_gitlab_repo(self, name: str, description: str, private: bool, token: str) -> Optional[str]:
        """Create repository via GitLab API"""
        url = "https://gitlab.com/api/v4/projects"
        headers = {"PRIVATE-TOKEN": token}
        data = {
            "name": name,
            "description": description,
            "visibility": "private" if private else "public",
            "initialize_with_readme": "false"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            if response.status_code == 201:
                repo_info = response.json()
                logger.info(f"GitLab repository created: {repo_info['web_url']}")
                return repo_info["http_url_to_repo"]
            else:
                logger.error(f"GitLab repo creation failed: {response.text}")
                return None

    @retry(retries=3, delay=5.0)
    async def push_to_remote(self, path: str, remote_url: str, branch: str = "main") -> bool:
         """Push local repo to remote asynchronously"""
         try:
             # Add remote
             await run_command_async(["git", "remote", "add", "origin", remote_url], cwd=path)
             
             # Add all files
             await run_command_async(["git", "add", "."], cwd=path)
             
             # Commit
             await run_command_async(["git", "commit", "-m", "Initial commit"], cwd=path)
             
             # Push
             code, stdout, stderr = await run_command_async(["git", "push", "-u", "origin", branch], cwd=path)
             if code != 0:
                 logger.error(f"Push failed: {stderr}")
                 return False
                 
             logger.info(f"Pushed to {remote_url}")
             return True
         except Exception as e:
             logger.error(f"Failed to push to remote: {e}")
             return False

    async def create_ghost_branch(self, path: str, base_branch: str = "main") -> str:
        """Create a temporary 'ghost' branch for AI changes asynchronously"""
        ghost_name = f"ai-ghost-{int(time.time())}"
        try:
            code, stdout, stderr = await run_command_async(["git", "checkout", "-b", ghost_name, base_branch], cwd=path)
            if code == 0:
                logger.info(f"Ghost branch {ghost_name} created from {base_branch}")
                return ghost_name
            return base_branch
        except Exception as e:
            logger.error(f"Failed to create ghost branch: {e}")
            return base_branch

    async def merge_ghost(self, path: str, ghost_branch: str, target_branch: str = "main"):
        """Merge ghost branch back with automatic conflict detection (Async)"""
        try:
            await run_command_async(["git", "checkout", target_branch], cwd=path)
            code, stdout, stderr = await run_command_async(["git", "merge", ghost_branch], cwd=path)
            
            if code != 0:
                logger.warning(f"Merge conflict detected merging {ghost_branch} into {target_branch}")
                conflicts = await self._get_conflicted_files(path)
                return {
                    "status": "conflict",
                    "conflicted_files": conflicts,
                    "message": "Automatic merge failed; manual or AI resolution required."
                }
            
            # Cleanup ghost branch after successful merge
            await run_command_async(["git", "branch", "-d", ghost_branch], cwd=path)
            return {"status": "success", "message": f"Successfully merged {ghost_branch}"}
        except Exception as e:
            logger.error(f"Merge error: {e}")
            return {"status": "error", "message": str(e)}

    async def _get_conflicted_files(self, path: str) -> list:
        """Get list of files with merge conflicts asynchronously"""
        try:
            code, stdout, stderr = await run_command_async(["git", "diff", "--name-only", "--diff-filter=U"], cwd=path)
            return stdout.splitlines() if code == 0 else []
        except:
            return []

    async def ai_resolve_conflict(self, path: str, file_path: str, orchestrator) -> bool:
        """Use AI to resolve a merge conflict asynchronously"""
        full_path = Path(path) / file_path
        if not full_path.exists(): return False
        
        try:
            content = full_path.read_text()
            if "<<<<<<<" not in content:
                return True # Already resolved?
                
            prompt = f"""
            Resolve the following git merge conflict in {file_path}.
            Choose the better implementation or merge them logically if possible.
            
            CONFLICTED CONTENT:
            {content}
            
            Respond only with the resolved file content, no explanations.
            """
            
            result = await orchestrator.run_inference(prompt=prompt, task_type="fix")
            resolved_content = result.get("output", "")
            
            if resolved_content and "<<<<<<<" not in resolved_content:
                full_path.write_text(resolved_content)
                await run_command_async(["git", "add", file_path], cwd=path)
                return True
                
            return False
        except Exception as e:
            logger.error(f"AI conflict resolution failed for {file_path}: {e}")
            return False
