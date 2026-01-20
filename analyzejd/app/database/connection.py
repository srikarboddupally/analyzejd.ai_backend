# app/database/connection.py
"""
Database connection and session management.
Uses SQLite for simplicity - no additional setup required.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database URL - SQLite file in the project root
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analyzejd.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
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
