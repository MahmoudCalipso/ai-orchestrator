"""
Git Sync Service
Handles Git operations for project management
"""
import logging
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GitSyncService:
    """Handles Git clone, pull, push operations"""
    
    def __init__(self):
        # Load Git user configuration from environment
        self.git_user_name = os.getenv("GIT_USER_NAME", "AI Orchestrator")
        self.git_user_email = os.getenv("GIT_USER_EMAIL", "ai-orchestrator@example.com")
    
    def _configure_git_user(self, local_path: str):
        """Configure Git user for a repository"""
        try:
            subprocess.run(
                ["git", "-C", local_path, "config", "user.name", self.git_user_name],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "-C", local_path, "config", "user.email", self.git_user_email],
                check=True,
                capture_output=True
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
        """Clone a Git repository"""
        try:
            local_path_obj = Path(local_path)
            local_path_obj.mkdir(parents=True, exist_ok=True)
            
            # Build clone command
            if credentials and credentials.get("token"):
                # Insert token into URL for HTTPS
                if "https://" in repo_url:
                    repo_url_with_token = repo_url.replace(
                        "https://",
                        f"https://{credentials['token']}@"
                    )
                else:
                    repo_url_with_token = repo_url
            else:
                repo_url_with_token = repo_url
            
            # Clone command
            cmd = [
                "git", "clone",
                "--branch", branch,
                repo_url_with_token,
                str(local_path)
            ]
            
            logger.info(f"Cloning repository from {repo_url} to {local_path}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Failed to clone repository"
                }
            
            # Get commit hash
            commit_hash = self._get_current_commit(local_path)
            
            # Configure Git user for this repository
            self._configure_git_user(local_path)
            
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
            
        except subprocess.TimeoutExpired:
            logger.error("Git clone timeout")
            return {
                "success": False,
                "error": "Clone operation timed out",
                "message": "Repository clone took too long"
            }
        except Exception as e:
            logger.error(f"Git clone error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to clone repository"
            }
    
    async def pull_latest(self, local_path: str) -> Dict[str, Any]:
        """Pull latest changes from remote"""
        try:
            cmd = ["git", "-C", local_path, "pull"]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            commit_hash = self._get_current_commit(local_path)
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "output": result.stdout
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
        commit_message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """Add, commit, and push changes"""
        try:
            # Add all changes
            subprocess.run(
                ["git", "-C", local_path, "add", "."],
                check=True,
                capture_output=True
            )
            
            # Commit
            subprocess.run(
                ["git", "-C", local_path, "commit", "-m", commit_message],
                check=True,
                capture_output=True
            )
            
            # Push
            result = subprocess.run(
                ["git", "-C", local_path, "push", "origin", branch],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr
                }
            
            commit_hash = self._get_current_commit(local_path)
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "message": "Changes pushed successfully"
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git push error: {e.stderr}")
            return {
                "success": False,
                "error": e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
            }
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_current_commit(self, local_path: str) -> str:
        """Get current commit hash"""
        try:
            result = subprocess.run(
                ["git", "-C", local_path, "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return ""
    
    async def get_status(self, local_path: str) -> Dict[str, Any]:
        """Get Git status"""
        try:
            result = subprocess.run(
                ["git", "-C", local_path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            
            has_changes = bool(result.stdout.strip())
            
            return {
                "success": True,
                "has_changes": has_changes,
                "status": result.stdout
            }
        except Exception as e:
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
        """Add, commit, and push changes to remote repository"""
        try:
            # Add all changes
            subprocess.run(
                ["git", "-C", local_path, "add", "."],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Check if there are changes to commit
            status_result = subprocess.run(
                ["git", "-C", local_path, "status", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "committed": False
                }
            
            # Commit changes
            subprocess.run(
                ["git", "-C", local_path, "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Push to remote
            push_result = subprocess.run(
                ["git", "-C", local_path, "push", "origin", branch],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if push_result.returncode != 0:
                logger.error(f"Git push failed: {push_result.stderr}")
                return {
                    "success": False,
                    "error": push_result.stderr,
                    "message": "Failed to push to remote"
                }
            
            # Get new commit hash
            commit_hash = self._get_current_commit(local_path)
            
            logger.info(f"Successfully pushed changes to {branch}")
            
            return {
                "success": True,
                "message": "Changes pushed successfully",
                "committed": True,
                "commit_hash": commit_hash,
                "branch": branch
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Git push timeout")
            return {
                "success": False,
                "error": "Push operation timed out",
                "message": "Push took too long"
            }
        except Exception as e:
            logger.error(f"Git push error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to push changes"
            }
