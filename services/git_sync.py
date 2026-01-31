"""
Git Sync Service
Handles Git operations for project management with non-blocking async execution.
"""
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from core.utils.subprocess import run_command_async

logger = logging.getLogger(__name__)


class GitSyncService:
    """Handles Git clone, pull, push operations asynchronously"""
    
    def __init__(self):
        # Load Git user configuration from environment
        self.git_user_name = os.getenv("GIT_USER_NAME", "AI Orchestrator")
        self.git_user_email = os.getenv("GIT_USER_EMAIL", "ai-orchestrator@example.com")
    
    async def _configure_git_user(self, local_path: str):
        """Configure Git user for a repository asynchronously"""
        try:
            await run_command_async(
                ["git", "-C", local_path, "config", "user.name", self.git_user_name],
                timeout=10
            )
            await run_command_async(
                ["git", "-C", local_path, "config", "user.email", self.git_user_email],
                timeout=10
            )
            logger.info(f"Configured Git user: {self.git_user_name} <{self.git_user_email}>")
        except Exception as e:
            logger.warning(f"Failed to configure Git user: {e}")
    
    async def clone_repository(
        self,
        repo_url: str,
        local_path: str,
        branch: str = "main",
        credentials: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Clone a Git repository asynchronously"""
        try:
            local_path_obj = Path(local_path)
            local_path_obj.mkdir(parents=True, exist_ok=True)
            
            # Use credentials if provided
            url = repo_url
            if credentials and credentials.get("token"):
                if "https://" in url:
                    url = url.replace("https://", f"https://{credentials['token']}@")
            
            # Clone command
            cmd = [
                "git", "clone",
                "--branch", branch,
                url,
                str(local_path)
            ]
            
            logger.info(f"Cloning repository from {repo_url} to {local_path}")
            
            code, stdout, stderr = await run_command_async(
                cmd,
                timeout=300  # 5 minutes timeout
            )
            
            if code != 0:
                logger.error(f"Git clone failed: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "message": "Failed to clone repository"
                }
            
            # Configure Git user for this repository
            await self._configure_git_user(local_path)
            
            # Get commit hash
            commit_hash = await self._get_current_commit(local_path)
            
            # Count files
            files_count = sum(1 for _ in Path(local_path).rglob('*') if _.is_file())
            
            logger.info(f"Successfully cloned repository. Commit: {commit_hash}, Files: {files_count}")
            
            return {
                "success": True,
                "local_path": local_path,
                "commit_hash": commit_hash,
                "files_count": files_count,
                "branch": branch
            }
            
        except Exception as e:
            logger.error(f"Git clone error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clone repository"
            }
    
    async def pull_latest(self, local_path: str) -> Dict[str, Any]:
        """Pull latest changes asynchronously"""
        try:
            code, stdout, stderr = await run_command_async(
                ["git", "-C", local_path, "pull"],
                timeout=60
            )
            
            if code != 0:
                return {
                    "success": False,
                    "error": stderr
                }
            
            commit_hash = await self._get_current_commit(local_path)
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "output": stdout
            }
            
        except Exception as e:
            logger.error(f"Git pull error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def push_changes(
        self,
        local_path: str,
        branch: str = "main",
        commit_message: str = "Update from AI Orchestrator"
    ) -> Dict[str, Any]:
        """Add, commit, and push changes asynchronously"""
        try:
            # Add
            await run_command_async(["git", "-C", local_path, "add", "."], timeout=30)
            
            # Check status
            code, stdout, stderr = await run_command_async(["git", "-C", local_path, "status", "--porcelain"], timeout=10)
            
            if code != 0:
                logger.error(f"Git status failed: {stderr}")
                return {
                    "success": False,
                    "error": stderr,
                    "message": "Failed to get git status"
                }

            if not stdout.strip():
                return {"success": True, "message": "No changes to commit", "committed": False}
            
            # Commit
            commit_code, _, commit_stderr = await run_command_async(["git", "-C", local_path, "commit", "-m", commit_message], timeout=30)
            if commit_code != 0:
                logger.error(f"Git commit failed: {commit_stderr}")
                return {
                    "success": False,
                    "error": commit_stderr,
                    "message": "Failed to commit changes"
                }
            
            # Push to remote
            push_code, push_stdout, push_stderr = await run_command_async(
                ["git", "-C", local_path, "push", "origin", branch],
                timeout=120
            )
            
            if push_code != 0:
                logger.error(f"Git push failed: {push_stderr}")
                return {
                    "success": False,
                    "error": push_stderr,
                    "message": "Failed to push to remote"
                }
            
            # Get new commit hash
            commit_hash = await self._get_current_commit(local_path)
            
            logger.info(f"Successfully pushed changes to {branch}")
            
            return {
                "success": True,
                "message": "Changes pushed successfully",
                "committed": True,
                "commit_hash": commit_hash,
                "branch": branch
            }
            
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to push changes"
            }

    async def list_branches(self, local_path: str) -> Dict[str, Any]:
        """List all branches asynchronously and return parsed data"""
        try:
            code, stdout, stderr = await run_command_async(["git", "-C", local_path, "branch", "-a"], timeout=10)
            if code != 0:
                return {"success": False, "error": stderr}
            
            branches = []
            current_branch = None
            
            for line in stdout.strip().split('\n'):
                line = line.strip()
                if not line: continue
                
                is_current = line.startswith('*')
                name = line[2:] if is_current else line
                
                branches.append({"name": name, "current": is_current})
                if is_current:
                    current_branch = name
            
            return {
                "success": True, 
                "branches": branches, 
                "current_branch": current_branch
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def checkout_branch(self, local_path: str, branch: str, create: bool = False) -> Dict[str, Any]:
        """Checkout a branch asynchronously"""
        try:
            cmd = ["git", "-C", local_path, "checkout"]
            
            if create:
                cmd.append("-b")
            
            cmd.append(branch)
            
            code, stdout, stderr = await run_command_async(cmd, timeout=30)
            if code != 0:
                # If checkout failed and we didn't specify create, maybe it needs -b?
                if not create and "did not match any file(s) known to git" in stderr:
                    cmd.insert(4, "-b") # git -C path checkout -b branch
                    code, stdout, stderr = await run_command_async(cmd, timeout=30)
                    if code != 0:
                        return {"success": False, "error": stderr}
                else:
                    return {"success": False, "error": stderr}
            
            return {"success": True, "branch": branch, "output": stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def merge_branches(self, local_path: str, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Merge branches asynchronously"""
        try:
            # Checkout target branch first
            await run_command_async(["git", "-C", local_path, "checkout", target_branch], timeout=30)
            
            # Merge source into target
            code, stdout, stderr = await run_command_async(["git", "-C", local_path, "merge", source_branch], timeout=60)
            
            if code != 0:
                return {
                    "success": False,
                    "error": stderr,
                    "output": stdout,
                    "message": "Merge conflict or error detected"
                }
            
            return {
                "success": True,
                "message": f"Successfully merged {source_branch} into {target_branch}",
                "output": stdout
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_current_commit(self, local_path: str) -> str:
        """Get current commit hash asynchronously"""
        code, stdout, stderr = await run_command_async(
            ["git", "-C", local_path, "rev-parse", "HEAD"],
            timeout=10
        )
        return stdout.strip() if code == 0 else ""

    async def get_status(self, local_path: str) -> Dict[str, Any]:
        """Get Git status asynchronously"""
        code, stdout, stderr = await run_command_async(
            ["git", "-C", local_path, "status", "--porcelain"],
            timeout=10
        )
        
        has_changes = bool(stdout.strip())
        
        return {
            "success": code == 0,
            "has_changes": has_changes,
            "status": stdout,
            "error": stderr if code != 0 else None
        }

    async def get_history(self, local_path: str, limit: int = 50) -> Dict[str, Any]:
        """Get commit history asynchronously"""
        try:
            cmd = ["git", "-C", local_path, "log", f"-n {limit}", "--pretty=format:%H|%an|%ae|%at|%s"]
            code, stdout, stderr = await run_command_async(cmd, timeout=30)
            
            if code != 0:
                return {"success": False, "error": stderr}
                
            commits = []
            for line in stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        h, an, ae, at, s = parts
                        commits.append({
                            "hash": h,
                            "author": an,
                            "email": ae,
                            "timestamp": int(at),
                            "subject": s
                        })
            
            return {"success": True, "commits": commits}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_diff(self, local_path: str, cached: bool = False) -> Dict[str, Any]:
        """Get current diff asynchronously"""
        try:
            cmd = ["git", "-C", local_path, "diff"]
            if cached:
                cmd.append("--cached")
            
            code, stdout, stderr = await run_command_async(cmd, timeout=30)
            return {"success": code == 0, "diff": stdout, "error": stderr if code != 0 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def fetch_remote(self, local_path: str) -> Dict[str, Any]:
        """Fetch from remote asynchronously"""
        try:
            code, stdout, stderr = await run_command_async(["git", "-C", local_path, "fetch", "origin"], timeout=60)
            return {"success": code == 0, "message": "Fetched successfully" if code == 0 else "Fetch failed", "error": stderr if code != 0 else None}
        except Exception as e:
            return {"success": False, "error": str(e)}
