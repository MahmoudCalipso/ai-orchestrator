"""
SQLAlchemy base models and session management
"""
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
import os

class Base(DeclarativeBase):
    pass

# Use shared engine and session from platform core
from platform_core.database import engine, SessionLocal, Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
