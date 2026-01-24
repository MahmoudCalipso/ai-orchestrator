"""
Project Manager Service
Handles CRUD operations for user projects
"""
import logging
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class ProjectManager:
    """Manages user projects"""
    
    def __init__(self, storage_base_path: str = "./storage/projects"):
        self.storage_base_path = Path(storage_base_path)
        self.storage_base_path.mkdir(parents=True, exist_ok=True)
        self.projects_db: Dict[str, Dict[str, Any]] = {}  # In-memory for now
        
    def create_project(
        self,
        user_id: str,
        project_name: str,
        description: str = "",
        git_repo_url: str = "",
        language: str = "",
        framework: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new project"""
        project_id = str(uuid.uuid4())
        
        # Create local path
        local_path = self.storage_base_path / user_id / project_name.replace(" ", "_").lower()
        local_path.mkdir(parents=True, exist_ok=True)
        
        project = {
            "id": project_id,
            "user_id": user_id,
            "project_name": project_name,
            "description": description,
            "git_repo_url": git_repo_url,
            "git_branch": kwargs.get("git_branch", "main"),
            "local_path": str(local_path),
            "status": "active",
            "language": language,
            "framework": framework,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_opened_at": None,
            "build_status": None,
            "run_status": None,
            "metadata": kwargs.get("metadata", {})
        }
        
        self.projects_db[project_id] = project
        logger.info(f"Created project {project_id} for user {user_id}")
        
        return project
    
    def get_user_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get all projects for a user with advanced filtering"""
        user_projects = [
            p for p in self.projects_db.values()
            if p["user_id"] == user_id
        ]
        
        # Apply filters
        if status:
            user_projects = [p for p in user_projects if p["status"] == status]
            
        if filters:
            if filters.get("name"):
                name_query = filters["name"].lower()
                user_projects = [p for p in user_projects if name_query in p["project_name"].lower()]
            
            if filters.get("framework"):
                target = filters["framework"]
                if isinstance(target, list):
                    user_projects = [p for p in user_projects if p.get("framework") in target]
                else:
                    user_projects = [p for p in user_projects if p.get("framework") == target]
                    
            if filters.get("language"):
                target = filters["language"]
                if isinstance(target, list):
                    user_projects = [p for p in user_projects if p.get("language") in target]
                else:
                    user_projects = [p for p in user_projects if p.get("language") == target]
            
            if filters.get("solution_id"):
                # This would typically be a DB join, but for in-memory:
                # We need to check if solution_id is in project metadata or a separate mapping
                sol_id = filters["solution_id"]
                user_projects = [p for p in user_projects if p.get("metadata", {}).get("solution_id") == sol_id]

        # Sort by last_opened_at or updated_at
        user_projects.sort(
            key=lambda x: x.get("last_opened_at") or x.get("updated_at", ""),
            reverse=True
        )
        
        # Pagination
        total = len(user_projects)
        start = (page - 1) * page_size
        end = start + page_size
        projects = user_projects[start:end]
        
        return {
            "projects": projects,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project"""
        return self.projects_db.get(project_id)
    
    def update_project(self, project_id: str, **updates) -> Optional[Dict[str, Any]]:
        """Update project fields"""
        project = self.projects_db.get(project_id)
        if not project:
            return None
        
        project.update(updates)
        project["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated project {project_id}")
        return project
    
    def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project"""
        project = self.projects_db.get(project_id)
        if not project or project["user_id"] != user_id:
            return False
        
        # Remove from database
        del self.projects_db[project_id]
        
        # Optionally delete local files (be careful!)
        # local_path = Path(project["local_path"])
        # if local_path.exists():
        #     shutil.rmtree(local_path)
        
        logger.info(f"Deleted project {project_id}")
        return True
    
    def update_last_opened(self, project_id: str):
        """Update last opened timestamp"""
        project = self.projects_db.get(project_id)
        if project:
            project["last_opened_at"] = datetime.utcnow().isoformat()
            project["updated_at"] = datetime.utcnow().isoformat()
    
    def update_build_status(self, project_id: str, status: str):
        """Update build status"""
        project = self.projects_db.get(project_id)
        if project:
            project["build_status"] = status
            project["updated_at"] = datetime.utcnow().isoformat()
    
    def update_run_status(self, project_id: str, status: str):
        """Update run status"""
        project = self.projects_db.get(project_id)
        if project:
            project["run_status"] = status
            project["updated_at"] = datetime.utcnow().isoformat()
