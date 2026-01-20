# app/main.py
"""
AnalyzeJD API - FastAPI application with database integration.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from app.schemas import AnalyzeRequest, FinalAnalysisResponse
from app.services.pass1_quick import run_quick_pass
from app.services.pass2_deep import run_deep_pass
from app.database.connection import get_db, init_db
from app.database import crud

# Initialize FastAPI app
app = FastAPI(
    title="AnalyzeJD API",
    description="AI-powered job description analyzer for Indian tech freshers",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()


# --- Health Check ---

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AnalyzeJD API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "POST /analyze",
            "history": "GET /analyses",
            "get_analysis": "GET /analyses/{id}"
        }
    }


# --- Main Analysis Endpoint ---

@app.post("/analyze")
def analyze_jd(payload: dict, db: Session = Depends(get_db)):
    """
    Analyze a job description and return detailed insights.
    Automatically saves the analysis to the database.
    """
    jd_text = payload.get("job_description", "")
    
    if not jd_text or len(jd_text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description must be at least 50 characters"
        )
    
    # Run analysis pipeline
    quick = run_quick_pass(jd_text)
    deep = run_deep_pass(jd_text, quick)
    
    # Convert to dict for storage
    result_dict = deep.model_dump()
    
    # Save to database
    analysis = crud.create_analysis(
        db=db,
        jd_text=jd_text,
        company_name=result_dict.get("understanding", {}).get("company", {}).get("name"),
        company_type=result_dict.get("understanding", {}).get("company", {}).get("type"),
        recommendation=result_dict.get("decision_guidance", {}).get("recommendation"),
        risk_level=result_dict.get("risk_and_tradeoffs", {}).get("risk_level"),
        fresher_alignment=result_dict.get("experience_fit", {}).get("fresher_alignment"),
        confidence_score=result_dict.get("confidence", {}).get("overall_confidence"),
        full_result=result_dict
    )
    
    # Add analysis ID to response
    result_dict["id"] = analysis.id
    
    return result_dict


# --- History Endpoints ---

@app.get("/analyses")
def get_analyses(
    skip: int = 0,
    limit: int = 20,
    recommendation: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of past analyses."""
    analyses = crud.get_analyses(db, skip=skip, limit=limit, recommendation=recommendation)
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "company_name": a.company_name,
                "company_type": a.company_type,
                "recommendation": a.recommendation,
                "risk_level": a.risk_level,
                "confidence_score": a.confidence_score,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "is_saved": a.is_saved
            }
            for a in analyses
        ]
    }


@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Get a specific analysis by ID."""
    analysis = crud.get_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "id": analysis.id,
        "jd_text": analysis.jd_text,
        "company_name": analysis.company_name,
        "company_type": analysis.company_type,
        "recommendation": analysis.recommendation,
        "risk_level": analysis.risk_level,
        "fresher_alignment": analysis.fresher_alignment,
        "confidence_score": analysis.confidence_score,
        "full_result": analysis.full_result,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "is_saved": analysis.is_saved
    }


@app.post("/analyses/{analysis_id}/save")
def save_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Mark an analysis as saved."""
    analysis = crud.save_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {"status": "saved", "id": analysis.id}


@app.delete("/analyses/{analysis_id}")
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    """Delete an analysis."""
    success = crud.delete_analysis(db, analysis_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {"status": "deleted", "id": analysis_id}


# --- Companies Endpoint ---

@app.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    """Get all known companies."""
    companies = crud.get_all_companies(db)
    
    return {
        "count": len(companies),
        "companies": [
            {
                "name": c.name,
                "type": c.type,
                "tier": c.tier,
                "aliases": c.aliases
            }
            for c in companies
        ]
    }


@app.post("/companies/seed")
def seed_companies(db: Session = Depends(get_db)):
    """Seed companies from the built-in database."""
    added = crud.seed_companies_from_extractor(db)
    return {"status": "seeded", "companies_added": added}
