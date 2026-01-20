# app/database/models.py
"""
SQLAlchemy models for AnalyzeJD.

Tables:
- analyses: Stores JD analysis results
- companies: Stores company classification data
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, Enum, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


# --- Enums ---

class CompanyType(str, enum.Enum):
    PRODUCT = "Product"
    SERVICE = "Service"
    STARTUP = "Startup"
    CAPTIVE = "Captive"
    UNKNOWN = "Unknown"


class CompanyTier(str, enum.Enum):
    FAANGM = "FAANGM"
    TIER_1 = "Tier-1"
    TIER_2 = "Tier-2"
    TIER_3 = "Tier-3"
    UNKNOWN = "Unknown"


class Recommendation(str, enum.Enum):
    APPLY = "Apply"
    CAUTION = "Apply with Caution"
    SKIP = "Skip"


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class FresherAlignment(str, enum.Enum):
    GOOD = "Good"
    POOR = "Poor"
    NOT_APPLICABLE = "Not Applicable"


# --- Models ---

class Analysis(Base):
    """Stores each JD analysis result."""
    __tablename__ = "analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Input
    jd_text = Column(Text, nullable=False)
    
    # Company info
    company_name = Column(String(255), nullable=True)
    company_type = Column(String(50), nullable=True)
    
    # Key decisions (for filtering/searching)
    recommendation = Column(String(50), nullable=True)
    risk_level = Column(String(50), nullable=True)
    fresher_alignment = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Full result (JSON blob)
    full_result = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_saved = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Analysis {self.id[:8]}... company={self.company_name}>"


class Company(Base):
    """Stores company classification data."""
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String(255), unique=True, nullable=False)
    aliases = Column(JSON, default=list)  # List of alternative names
    type = Column(String(50), nullable=False)
    tier = Column(String(50), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Company {self.name} type={self.type}>"
