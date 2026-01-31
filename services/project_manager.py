import logging
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import DatabaseManager
from models.user_project import UserProject
from platform_core.auth.models import User

logger = logging.getLogger(__name__)

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
    
    async def get_projects(
        self,
        user_ids: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get projects with RBAC-aware filtering.
        
        Args:
            user_ids: List of user IDs to filter by. None means all users (Super Admin).
            tenant_id: Filter by tenant ID (for Enterprise Admin scope).
            status: Filter by project status.
            page: Page number for pagination.
            page_size: Number of items per page.
            filters: Additional filters (name, framework, language, solution_id).
        
        Returns:
            Dict with projects, total count, and pagination info.
        """
        async with self.db_manager.session() as session:
            # Build base query with optional tenant join
            if tenant_id or user_ids is None:
                # Need to join with User to filter by tenant
                query = select(UserProject, User.tenant_id).join(User, UserProject.user_id == User.id)
            else:
                query = select(UserProject)
            
            # Apply user filter if specified
            if user_ids is not None:
                if len(user_ids) == 1:
                    query = query.where(UserProject.user_id == user_ids[0])
                else:
                    query = query.where(UserProject.user_id.in_(user_ids))
            
            # Apply tenant filter if specified
            if tenant_id:
                query = query.where(User.tenant_id == tenant_id)
            
            # Apply status filter
            if status:
                query = query.where(UserProject.status == status)
            
            # Apply additional filters
            if filters:
                if filters.get("name"):
                    query = query.where(
                        UserProject.project_name.ilike(f"%{filters['name']}%")
                    )
                if filters.get("framework"):
                    query = query.where(UserProject.framework == filters["framework"])
                if filters.get("language"):
                    query = query.where(UserProject.language == filters["language"])
            
            # Get total count before pagination
            count_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(count_query)
            total = total_result.scalar() or 0
            
            # Apply pagination
            query = query.order_by(UserProject.created_at.desc())
            query = query.offset((page - 1) * page_size).limit(page_size)
            
            result = await session.execute(query)
            
            # Extract projects from result (handle tuple with tenant_id if joined)
            rows = result.all()
            projects_list = []
            for row in rows:
                if isinstance(row, tuple):
                    projects_list.append(row[0])  # UserProject is first element
                else:
                    projects_list.append(row)
            
            return {
                "projects": [p.to_dict() for p in projects_list],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    
    async def get_user_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get all projects for a specific user via the repository.
        This is a convenience wrapper around get_projects for single-user queries.
        """
        return await self.get_projects(
            user_ids=[user_id],
            status=status,
            page=page,
            page_size=page_size,
            filters=filters
        )
    
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
