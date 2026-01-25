import os
import sys
import logging
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

from platform_core.database import Base, engine as default_engine
from platform_core.auth.models import User, APIKey, RefreshToken, ExternalAccount, PasswordResetToken
from platform_core.tenancy.models import Tenant
from services.registry.persistence import FrameworkMetadata, LanguageMetadata, DatabaseMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_postgres(args):
    # Support both command line override and .env variable
    db_url = os.getenv("DATABASE_URL")
    
    if args.host:
        # Command line override construction
        db_url = f"postgresql://{args.user}:{args.password}@{args.host}:{args.port}/{args.dbname}"
    
    if not db_url:
        print("ERROR: DATABASE_URL not set in environment and no CLI overrides provided.")
        sys.exit(1)
        
    print(f"Connecting to PostgreSQL using DATABASE_URL configuration...")
    
    try:
        # Create temporary engine for initialization
        temp_engine = create_engine(db_url)
        
        # 1. Test connection
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✓ Connection successful.")
            
        # 2. Create tables
        print("Creating tables...")
        Base.metadata.create_all(bind=temp_engine)
        print("✓ All tables created.")
        
        # 3. Initialize default registry data
        # We need to temporarily patch SessionLocal to use our db_url
        from platform_core import database
        original_session = database.SessionLocal
        database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=temp_engine)
        
        from services.registry.framework_registry import FrameworkRegistry
        registry = FrameworkRegistry()
        print("✓ Framework registry initialized with defaults in PostgreSQL.")
        
        # Restore original session
        database.SessionLocal = original_session
        
        print("\nPostgreSQL setup complete!")
        print(f"IMPORTANT: Ensure your .env file has: DATABASE_URL={db_url}")
        
    except Exception as e:
        print(f"\nFAILED to setup PostgreSQL: {e}")
        print("\nPossible solutions:")
        print("1. Ensure PostgreSQL is installed and running.")
        print("2. Ensure the database 'ai_orchestrator' exists (run: CREATE DATABASE ai_orchestrator;)")
        print("3. Check your credentials (user/password).")
        print("\nUsage example:")
        print("python scripts/setup_postgres.py --host myhost --port 5432 --user myuser --password mypass")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Orchestrator PostgreSQL Setup")
    parser.add_argument("--host", help="PostgreSQL host")
    parser.add_argument("--port", default="5432", help="PostgreSQL port")
    parser.add_argument("--user", default="postgres", help="PostgreSQL user")
    parser.add_argument("--password", default="postgres", help="PostgreSQL password")
    parser.add_argument("--dbname", default="ai_orchestrator", help="Database name")
    
    args = parser.parse_args()
    
    import asyncio
    asyncio.run(setup_postgres(args))
