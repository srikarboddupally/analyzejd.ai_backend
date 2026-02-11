# app/database/connection.py
"""
Database connection and session management.
Supports both SQLite (local) and PostgreSQL (Render/Prod).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database URL - default to SQLite file in the project root
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analyzejd.db")

# Fix for Render's postgres:// URI (SQLAlchemy requires postgresql://)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Check if we are using SQLite
is_sqlite = DATABASE_URL.startswith("sqlite")

# Create engine
engine_kwargs = {}
if is_sqlite:
    # Needed for SQLite
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    **engine_kwargs
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use with FastAPI's Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.database.models import Base
    Base.metadata.create_all(bind=engine)
