"""
SQLAlchemy base models and session management
"""
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os

class Base(DeclarativeBase):
    pass

# Default to SQLite for internal registry persistence if no DB is configured
DB_PATH = os.path.join(os.getcwd(), "storage", "registry.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
