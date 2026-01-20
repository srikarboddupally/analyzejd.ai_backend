# app/database/__init__.py
"""
Database package for AnalyzeJD.
Uses SQLite with SQLAlchemy for simplicity.
"""

from app.database.connection import get_db, engine, SessionLocal
from app.database.models import Base, Analysis, Company

__all__ = ["get_db", "engine", "SessionLocal", "Base", "Analysis", "Company"]
