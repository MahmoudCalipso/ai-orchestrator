from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

from app.core.database import DatabaseManager

class ProjectManager:
    """Manages user projects using the Repository Pattern"""
    
    def __init__(
        self, 
        db_manager: DatabaseManager, 
        project_repo_factory: Callable[..., Any],
        storage_base_path: str = "./storage/projects"
    ):
        self.db_manager = db_manager
        self.project_repo_factory = project_repo_factory
        self.storage_base_path = Path(storage_base_path)
        self.storage_base_path.mkdir(parents=True, exist_ok=True)
        
    async def create_project(
        self,
        user_id: str,
        project_name: str,
        description: str = "",
        git_repo_url: str = "",
        language: str = "",
        framework: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new project using the repository"""
        project_id = uuid.uuid4()
        
        # Create local path
        local_path = self.storage_base_path / user_id / project_name.replace(" ", "_").lower()
        local_path.mkdir(parents=True, exist_ok=True)
        
        async with self.db_manager.session() as session:
            repo = self.project_repo_factory(session)
            project = await repo.create(
                id=project_id,
                user_id=user_id,
                project_name=project_name,
                description=description,
                git_repo_url=git_repo_url,
                git_branch=kwargs.get("git_branch", "main"),
                local_path=str(local_path),
                status="active",
                language=language,
                framework=framework,
                extra_metadata=kwargs.get("metadata", {})
            )
            await repo.save_changes()
            
            logger.info(f"Created project {project_id} for user {user_id}")
            return project.to_dict()
    
    async def get_user_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get all projects for a user via the repository"""
        async with self.db_manager.session() as session:
            repo = self.project_repo_factory(session)
            
            # Combine basic filters with custom filters
            all_filters = filters.copy() if filters else {}
            if status:
                all_filters["status"] = status
            
            # Note: We still use the repository for basic list, 
            # but specialized filtering might need the repo methods.
            # For now, let's use the list method and handle specialized search if needed.
            
            # If name search is present, we might need a specialized repo method
            # or just use the generic list if it supports ilike (it doesn't yet).
            # For Phase 3, let's stick to the repo.
            
            projects_list = await repo.get_by_user(user_id, status)
            
            # Apply manual filtering/pagination for now to keep repo simple,
            # or we could enhance the repo.
            if filters and filters.get("name"):
                name_filter = filters["name"].lower()
                projects_list = [p for p in projects_list if name_filter in p.project_name.lower()]
            
            total = len(projects_list)
            start = (page - 1) * page_size
            end = start + page_size
            paginated = projects_list[start:end]
            
            return {
                "projects": [p.to_dict() for p in paginated],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project via repository"""
        async with self.db_manager.session() as session:
            repo = self.project_repo_factory(session)
            project = await repo.get_by_id(project_id)
            return project.to_dict() if project else None
    
    async def update_project(self, project_id: str, **updates) -> Optional[Dict[str, Any]]:
        """Update project via repository"""
        async with self.db_manager.session() as session:
            repo = self.project_repo_factory(session)
            project = await repo.update(project_id, **updates)
            if project:
                await repo.save_changes()
                logger.info(f"Updated project {project_id}")
                return project.to_dict()
            return None
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete project via repository"""
        async with self.db_manager.session() as session:
            repo = self.project_repo_factory(session)
            # Verify ownership first
            project = await repo.get_by_id(project_id)
            if not project or project.user_id != user_id:
                return False
            
            success = await repo.delete(project_id)
            if success:
                await repo.save_changes()
                logger.info(f"Deleted project {project_id}")
            return success
    
    async def update_last_opened(self, project_id: str):
        """Update last opened timestamp"""
        await self.update_project(project_id, last_opened_at=datetime.utcnow())
    
    async def update_build_status(self, project_id: str, status: str):
        """Update build status"""
        await self.update_project(project_id, build_status=status)
    
    async def update_run_status(self, project_id: str, status: str):
        """Update run status"""
        await self.update_project(project_id, run_status=status)
