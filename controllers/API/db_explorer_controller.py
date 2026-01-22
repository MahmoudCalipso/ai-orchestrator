"""
Database Explorer - API Controller
Allows frontend to introspect and query project databases.
Converted from legacy platform_core routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from platform_core.auth.dependencies import get_db, get_current_active_user, require_git_account
from platform_core.auth.models import User
from services.database.explorer import DatabaseExplorerService
from services.database.connection_manager import (
    DatabaseConnectionManager
)
from schemas.generation_spec import DatabaseConfig

router = APIRouter(prefix="/database-explorer", tags=["Database Explorer"])

# Initialized via dependency or singleton
db_manager = DatabaseConnectionManager()
explorer_service = DatabaseExplorerService(db_manager)

@router.post("/tables")
async def list_tables(
    config: DatabaseConfig,
    user: User = Depends(require_git_account)
):
    """List all tables in the project database"""
    try:
        tables = await explorer_service.list_tables(config)
        return {"status": "success", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/table/{table_name}/schema")
async def get_schema(
    table_name: str,
    config: DatabaseConfig,
    user: User = Depends(require_git_account)
):
    """Get schema for a specific table"""
    try:
        schema = await explorer_service.get_table_schema(config, table_name)
        return {"status": "success", "schema": schema}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/table/{table_name}/data")
async def get_data(
    table_name: str,
    config: DatabaseConfig,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user: User = Depends(require_git_account)
):
    """Get sample data from a table"""
    try:
        data = await explorer_service.get_table_data(config, table_name, limit, offset)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def execute_custom_query(
    config: DatabaseConfig,
    query: str = Query(...),
    user: User = Depends(require_git_account)
):
    """Execute a custom SQL SELECT query"""
    try:
        result = await explorer_service.execute_query(config, query)
        return {"status": "success", "result": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
