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


from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.user_project import UserProject, ProjectSession, ProjectUpdate
from app.core.database import DatabaseManager

class ProjectManager:
    """Manages user projects with database persistence"""
    
    def __init__(self, db_manager: DatabaseManager, storage_base_path: str = "./storage/projects"):
        self.db_manager = db_manager
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
        """Create a new project in the database"""
        project_id = uuid.uuid4()
        
        # Create local path
        local_path = self.storage_base_path / user_id / project_name.replace(" ", "_").lower()
        local_path.mkdir(parents=True, exist_ok=True)
        
        project = UserProject(
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
        
        async with self.db_manager.session() as session:
            session.add(project)
            await session.commit()
            await session.refresh(project)
            
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
        """Get all projects for a user with database-side filtering"""
        query = select(UserProject).where(UserProject.user_id == user_id)
        
        if status:
            query = query.where(UserProject.status == status)
            
        if filters:
            if filters.get("name"):
                query = query.where(UserProject.project_name.ilike(f"%{filters['name']}%"))
            if filters.get("framework"):
                query = query.where(UserProject.framework == filters["framework"])
            if filters.get("language"):
                query = query.where(UserProject.language == filters["language"])

        # Sorting
        query = query.order_by(UserProject.updated_at.desc())
        
        async with self.db_manager.session() as session:
            # Simple pagination implementation
            result = await session.execute(query)
            all_projects = result.scalars().all()
            
            total = len(all_projects)
            start = (page - 1) * page_size
            end = start + page_size
            projects = all_projects[start:end]
            
            return {
                "projects": [p.to_dict() for p in projects],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
    
    async def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific project from database"""
        async with self.db_manager.session() as session:
            result = await session.execute(select(UserProject).where(UserProject.id == project_id))
            project = result.scalar_one_or_none()
            return project.to_dict() if project else None
    
    async def update_project(self, project_id: str, **updates) -> Optional[Dict[str, Any]]:
        """Update project in database"""
        async with self.db_manager.session() as session:
            result = await session.execute(select(UserProject).where(UserProject.id == project_id))
            project = result.scalar_one_or_none()
            if not project:
                return None
            
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            project.updated_at = datetime.utcnow()
            await session.commit()
            await session.refresh(project)
            
        logger.info(f"Updated project {project_id}")
        return project.to_dict()
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project from database"""
        async with self.db_manager.session() as session:
            result = await session.execute(
                select(UserProject).where(UserProject.id == project_id, UserProject.user_id == user_id)
            )
            project = result.scalar_one_or_none()
            if not project:
                return False
            
            await session.delete(project)
            await session.commit()
            
        logger.info(f"Deleted project {project_id}")
        return True
    
    async def update_last_opened(self, project_id: str):
        """Update last opened timestamp"""
        await self.update_project(project_id, last_opened_at=datetime.utcnow())
    
    async def update_build_status(self, project_id: str, status: str):
        """Update build status"""
        await self.update_project(project_id, build_status=status)
    
    async def update_run_status(self, project_id: str, status: str):
        """Update run status"""
        await self.update_project(project_id, run_status=status)
