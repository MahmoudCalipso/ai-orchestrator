"""
Database Explorer Service
Provides deep introspection and data sampling for project-specific databases.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text, inspect
from services.database.connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class DatabaseExplorerService:
    def __init__(self, connection_manager: DatabaseConnectionManager):
        self.conn_manager = connection_manager

    async def list_tables(self, config: Any) -> List[str]:
        """List all tables in the database"""
        engine = await self._get_engine(config)
        inspector = inspect(engine)
        return inspector.get_table_names()

    async def get_table_schema(self, config: Any, table_name: str) -> List[Dict[str, Any]]:
        """Get detailed schema for a specific table with validation"""
        engine = await self._get_engine(config)
        
        # SECURITY: Validate table name
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Invalid table name: {table_name}")
            
        columns = inspector.get_columns(table_name)
        
        # Convert types to string for JSON serialization
        for col in columns:
            col['type'] = str(col['type'])
        return columns

    async def get_table_data(
        self, 
        config: Any, 
        table_name: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """Fetch sample data from a table with strict validation"""
        engine = await self._get_engine(config)
        
        # SECURITY: Validate table name against schema to prevent injection
        inspector = inspect(engine)
        if table_name not in inspector.get_table_names():
            raise ValueError(f"Invalid table name: {table_name}")
            
        query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
        
        with engine.connect() as conn:
            result = conn.execute(query, {"limit": limit, "offset": offset})
            columns = result.keys()
            data = [dict(zip(columns, row)) for row in result]
            
            # Get total count
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            total_count = conn.execute(count_query).scalar()
            
        return {
            "columns": list(columns),
            "rows": data,
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        }

    async def execute_query(self, config: Any, query_str: str) -> Dict[str, Any]:
        """Execute a read-only query (Safety enforcement suggested)"""
        # Basic SQL safety check: only allow SELECT
        if not query_str.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed for exploration.")
            
        engine = await self._get_engine(config)
        with engine.connect() as conn:
            result = conn.execute(text(query_str))
            if result.returns_rows:
                columns = result.keys()
                data = [dict(zip(columns, row)) for row in result]
                return {"columns": list(columns), "rows": data}
            return {"message": "Query executed successfully, no rows returned."}

    async def _get_engine(self, config: Any):
        """Helper to get or establish a connection engine"""
        engine = self.conn_manager.get_engine(config.database_name)
        if not engine:
            await self.conn_manager.connect(config)
            engine = self.conn_manager.get_engine(config.database_name)
        return engine

database_explorer = None # Initialized in main or dependency injection
