
import asyncio
import os
from services.database.explorer import DatabaseExplorerService
from services.database.connection_manager import DatabaseConnectionManager
from dotenv import load_dotenv

load_dotenv()

async def list_available_tables():
    conn_manager = DatabaseConnectionManager()
    explorer = DatabaseExplorerService(conn_manager)
    
    class MockConfig:
        def __init__(self):
            self.database_name = "ai_orchestrator"
            self.type = "postgresql"
            self.host = "127.0.0.1"
            self.port = 5432
            self.username = "orchestrator"
            self.password = "MAHMOUD1996*369*PgSqlPassWd"
            self.connection_string = None
    
    config = MockConfig()
    
    try:
        tables = await explorer.list_tables(config)
        print(f"Available tables: {tables}")
    except Exception as e:
        print(f"Failed to list tables: {e}")

if __name__ == "__main__":
    asyncio.run(list_available_tables())
