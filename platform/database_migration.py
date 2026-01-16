"""
Database Migration Script
Initialize authentication and multi-tenancy tables
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Import all models
from platform.auth.models import Base as AuthBase, User, APIKey, RefreshToken
from platform.tenancy.models import Base as TenantBase, Tenant


def create_tables():
    """Create all database tables"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_orchestrator")
    
    # Create engine
    engine = create_engine(database_url)
    
    # Create all tables
    print("Creating tenants table...")
    TenantBase.metadata.create_all(bind=engine, tables=[Tenant.__table__])
    
    print("Creating authentication tables...")
    AuthBase.metadata.create_all(bind=engine, tables=[
        User.__table__,
        APIKey.__table__,
        RefreshToken.__table__
    ])
    
    print("✅ All tables created successfully!")


def drop_tables():
    """Drop all database tables (use with caution!)"""
    
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_orchestrator")
    engine = create_engine(database_url)
    
    print("⚠️  Dropping all tables...")
    AuthBase.metadata.drop_all(bind=engine)
    TenantBase.metadata.drop_all(bind=engine)
    
    print("✅ All tables dropped!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Cancelled.")
    else:
        create_tables()
