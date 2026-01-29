
import asyncio
import os
from services.database.explorer import DatabaseExplorerService
from services.database.connection_manager import DatabaseConnectionManager
from dotenv import load_dotenv

load_dotenv()

async def test_sql_injection_fix():
    # Setup
    conn_manager = DatabaseConnectionManager()
    explorer = DatabaseExplorerService(conn_manager)
    
    # Mock config that behaves like DatabaseConfig
    class MockConfig:
        def __init__(self):
            self.database_name = "ai_orchestrator"
            self.type = "postgresql" # Changed from db_type to type
            self.host = "127.0.0.1"
            self.port = 5432
            self.username = "orchestrator"
            self.password = "MAHMOUD1996*369*PgSqlPassWd"
            self.connection_string = None # Added missing attribute
    
    config = MockConfig()
    
    print("Testing with valid table name...")
    try:
        # We know 'users' exists because the app started and create_tables was called
        data = await explorer.get_table_data(config, "users", limit=1)
        print(f"Success! Retrieved {len(data['rows'])} rows from 'users'.")
        print(f"Columns: {data['columns']}")
    except Exception as e:
        print(f"Failed to retrieve data from 'users': {e}")

    print("\nTesting with SQL injection attempt in table name...")
    # Attempting to inject: users; SELECT 1;
    malicious_table = "users; SELECT 1;"
    try:
        await explorer.get_table_data(config, malicious_table)
        print("CRITICAL FAILURE: Malicious table name was accepted!")
    except ValueError as ve:
        print(f"System correctly rejected malicious table name: {ve}")
    except Exception as e:
        print(f"Caught unexpected exception (likely SQL error if injection worked): {e}")

    print("\nTesting with non-existent table name...")
    try:
        await explorer.get_table_data(config, "non_existent_table")
        print("FAILURE: Non-existent table name was accepted!")
    except ValueError as ve:
        print(f"System correctly rejected non-existent table name: {ve}")

if __name__ == "__main__":
    asyncio.run(test_sql_injection_fix())
