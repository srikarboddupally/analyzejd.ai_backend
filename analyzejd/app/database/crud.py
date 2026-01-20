# app/database/crud.py
"""
CRUD operations for AnalyzeJD database.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.models import Analysis, Company
from datetime import datetime


# --- Analysis CRUD ---

def create_analysis(
    db: Session,
    jd_text: str,
    company_name: Optional[str],
    company_type: Optional[str],
    recommendation: Optional[str],
    risk_level: Optional[str],
    fresher_alignment: Optional[str],
    confidence_score: Optional[float],
    full_result: dict
) -> Analysis:
    """Create a new analysis record."""
    analysis = Analysis(
        jd_text=jd_text,
        company_name=company_name,
        company_type=company_type,
        recommendation=recommendation,
        risk_level=risk_level,
        fresher_alignment=fresher_alignment,
        confidence_score=confidence_score,
        full_result=full_result
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def get_analysis(db: Session, analysis_id: str) -> Optional[Analysis]:
    """Get a single analysis by ID."""
    return db.query(Analysis).filter(Analysis.id == analysis_id).first()


def get_analyses(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    recommendation: Optional[str] = None
) -> List[Analysis]:
    """Get list of analyses with optional filtering."""
    query = db.query(Analysis).order_by(Analysis.created_at.desc())
    
    if recommendation:
        query = query.filter(Analysis.recommendation == recommendation)
    
    return query.offset(skip).limit(limit).all()


def get_recent_analyses(db: Session, limit: int = 10) -> List[Analysis]:
    """Get most recent analyses."""
    return db.query(Analysis)\
        .order_by(Analysis.created_at.desc())\
        .limit(limit)\
        .all()


def save_analysis(db: Session, analysis_id: str) -> Optional[Analysis]:
    """Mark an analysis as saved."""
    analysis = get_analysis(db, analysis_id)
    if analysis:
        analysis.is_saved = True
        db.commit()
        db.refresh(analysis)
    return analysis


def delete_analysis(db: Session, analysis_id: str) -> bool:
    """Delete an analysis."""
    analysis = get_analysis(db, analysis_id)
    if analysis:
        db.delete(analysis)
        db.commit()
        return True
    return False


# --- Company CRUD ---

def create_company(
    db: Session,
    name: str,
    type: str,
    tier: str,
    aliases: List[str] = None
) -> Company:
    """Create a new company record."""
    company = Company(
        name=name,
        type=type,
        tier=tier,
        aliases=aliases or []
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_company(db: Session, name: str) -> Optional[Company]:
    """Get a company by name."""
    return db.query(Company).filter(Company.name == name).first()


def get_all_companies(db: Session) -> List[Company]:
    """Get all companies."""
    return db.query(Company).order_by(Company.name).all()


def seed_companies_from_extractor(db: Session):
    """
    Seed the companies table from the existing company_extractor.py database.
    Only adds companies that don't already exist.
    """
    from app.utils.company_extractor import COMPANY_DATABASE
    
    added = 0
    for key, data in COMPANY_DATABASE.items():
        existing = get_company(db, key)
        if not existing:
            create_company(
                db=db,
                name=key,
                type=data["type"],
                tier=data["tier"],
                aliases=data.get("aliases", [])
            )
            added += 1
    
    return added
