import os
import sys
import logging
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from platform_core.database import DATABASE_URL, engine, SessionLocal, Base
from platform_core.auth.models import User, APIKey, RefreshToken, ExternalAccount, PasswordResetToken
from platform_core.tenancy.models import Tenant
from services.registry.persistence import FrameworkMetadata, LanguageMetadata, DatabaseMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_postgres():
    print(f"Connecting to PostgreSQL at {DATABASE_URL}...")
    
    try:
        # 1. Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✓ Connection successful.")
            
        # 2. Create tables
        print("Creating tables...")
        # Note: In production use Alembic. create_all is fine for MVP/Setup.
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created.")
        
        # 3. Initialize default registry data if empty
        from services.registry.framework_registry import FrameworkRegistry
        registry = FrameworkRegistry()
        print("✓ Framework registry initialized with defaults in PostgreSQL.")
        
        print("PostgreSQL setup complete!")
        
    except Exception as e:
        print(f"FAILED to setup PostgreSQL: {e}")
        if "does not exist" in str(e):
            print("TIP: Make sure you created the database 'ai_orchestrator' in PostgreSQL.")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_postgres())
