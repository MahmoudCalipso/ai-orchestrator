from typing import Generic, TypeVar, Type, List, Optional, Any, Union, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete

T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Generic asynchronous repository for SQLAlchemy models.
    """
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: Union[str, UUID]) -> Optional[T]:
        """Fetch a single record by its primary key ID."""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self, 
        filters: Optional[Dict[str, Any]] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[T]:
        """List records with optional filtering and pagination."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **data) -> T:
        """Create a new record."""
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def update(self, id: Union[str, UUID], **data) -> Optional[T]:
        """Update an existing record by ID."""
        query = sqlalchemy_update(self.model).where(self.model.id == id).values(**data).returning(self.model)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, id: Union[str, UUID]) -> bool:
        """Delete a record by ID."""
        query = sqlalchemy_delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def save_changes(self):
        """Commit current transaction."""
        await self.session.commit()
