from typing import List, Optional, Any, Dict
from uuid import UUID
from sqlalchemy.future import select
from core.repository.base import BaseRepository
from models.user_project import UserProject, ProjectSession, WorkflowExecution

class ProjectRepository(BaseRepository[UserProject]):
    """
    Repository for managing UserProject and related entities.
    """
    def __init__(self, session):
        super().__init__(UserProject, session)

    async def get_by_user(self, user_id: str, status: Optional[str] = None) -> List[UserProject]:
        """Fetch all projects belonging to a specific user with optional status filter."""
        query = select(UserProject).where(UserProject.user_id == user_id)
        if status:
            query = query.where(UserProject.status == status)
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_active_sessions(self, project_id: UUID) -> List[ProjectSession]:
        """Fetch all active sessions for a specific project."""
        query = select(ProjectSession).where(
            ProjectSession.project_id == project_id,
            ProjectSession.status == "active"
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_workflow_executions(self, project_id: UUID) -> List[WorkflowExecution]:
        """Fetch execution history for a specific project's workflows."""
        query = select(WorkflowExecution).where(WorkflowExecution.project_id == project_id)
        query = query.order_by(WorkflowExecution.started_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_build_status(self, project_id: UUID, status: str):
        """Update the build status of a project."""
        from sqlalchemy import update
        await self.session.execute(
            update(UserProject)
            .where(UserProject.id == project_id)
            .values(build_status=status)
        )
        await self.session.flush()

    async def update_run_status(self, project_id: UUID, status: str):
        """Update the runtime status of a project."""
        from sqlalchemy import update
        await self.session.execute(
            update(UserProject)
            .where(UserProject.id == project_id)
            .values(run_status=status)
        )
        await self.session.flush()
