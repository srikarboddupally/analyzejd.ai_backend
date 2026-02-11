# app/schemas.py
"""
Pydantic schemas for AnalyzeJD API responses.

These schemas match the output format specified in the system prompt
for Indian JD analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


# --- Understanding Section ---

class Company(BaseModel):
    """Company identification and context."""
    name: str = Field(description="Company name extracted from JD")
    type: Literal["Product", "Service", "Startup", "Captive", "Unknown"] = Field(
        description="Company type classification"
    )
    context: str = Field(
        description="Plain-language explanation of what this company type usually means in India"
    )


class Understanding(BaseModel):
    """What the role is really about."""
    company: Company
    role_reality: str = Field(
        description="Clear, simple explanation of what this role actually involves day-to-day"
    )


# --- Experience Fit Section ---

class ExperienceFit(BaseModel):
    """How well the role aligns with fresher/early-career profiles."""
    required_experience: str = Field(description="Experience requirement from JD")
    fresher_alignment: Literal["Good", "Poor", "Not Applicable"] = Field(
        description="Whether this role makes sense for freshers"
    )
    explanation: str = Field(
        description="Why this role does or does not make sense for a fresher or early-career engineer"
    )


# --- Career Implications Section ---

class CareerImplications(BaseModel):
    """Long-term career impact of taking this role."""
    skills_you_will_build: List[str] = Field(
        description="Skills you will likely develop in this role"
    )
    skills_you_may_miss: List[str] = Field(
        description="Skills you may not get exposure to in this role"
    )
    long_term_impact: str = Field(
        description="Likely impact on future flexibility and growth"
    )


# --- Risk and Tradeoffs Section ---

class RiskAndTradeoffs(BaseModel):
    """Risk assessment and profile matching."""
    risk_level: Literal["Low", "Medium", "High"] = Field(
        description="Overall risk level for early-career engineers"
    )
    key_concerns: List[str] = Field(
        description="Specific concerns about this role"
    )
    good_for: str = Field(
        description="Specific profile this role suits well"
    )
    avoid_if: str = Field(
        description="Specific profile who should avoid this role"
    )


# --- Decision Guidance Section ---

class DecisionGuidance(BaseModel):
    """Final recommendation and reasoning."""
    recommendation: Literal["Apply", "Apply with Caution", "Skip"] = Field(
        description="Clear action recommendation"
    )
    reasoning: str = Field(
        description="Calm, mentor-style explanation for the recommendation"
    )
    what_to_do_instead: str = Field(
        description="Concrete alternative role or company type if skipping"
    )


# --- Resume Guidance Section ---

class ResumeGuidance(BaseModel):
    """ATS-optimized resume bullets."""
    ats_optimized_bullets: List[str] = Field(
        description="Exactly 3 ATS-optimized bullets tailored to this role type",
        min_length=3,
        max_length=3
    )


# --- Confidence Section ---

class Confidence(BaseModel):
    """Analysis confidence score."""
    overall_confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score between 0 and 1"
    )


# --- Final Response ---

class FinalAnalysisResponse(BaseModel):
    """Complete JD analysis response matching the system prompt schema."""
    understanding: Understanding
    experience_fit: ExperienceFit
    career_implications: CareerImplications
    risk_and_tradeoffs: RiskAndTradeoffs
    decision_guidance: DecisionGuidance
    resume_guidance: ResumeGuidance
    confidence: Confidence


# --- Request Schema ---

class AnalyzeRequest(BaseModel):
    """Request payload for /analyze endpoint."""
    job_description: str = Field(
        description="The full job description text to analyze",
        min_length=50
    )


# --- Quick Pass Schemas (for internal use) ---

class CandidateInsights(BaseModel):
    """Insights about what candidates typically discover after joining."""
    what_they_discover: str
    growth_potential: Literal["High", "Medium", "Low", "Unknown"]
    work_life_balance: Literal["Good", "Moderate", "Demanding", "Unknown"]
    learning_opportunities: str


class RiskAssessment(BaseModel):
    """Internal risk assessment from quick pass."""
    risk_level: Literal["Low", "Medium", "High", "Unknown"]
    concerns: List[str]
    positives: List[str]


class ConfidenceBreakdown(BaseModel):
    """Detailed confidence score breakdown."""
    company_recognition: float
    risk_signals: float
    role_clarity: float
    company_tier: float


class LLMExplanations(BaseModel):
    """LLM-generated explanations (decisions are overridden by deterministic logic)."""
    company_context: str = Field(default="", description="Rich context about the company")
    required_experience: str = Field(default="", description="LLM's analysis of experience requirements")
    role_reality: str = ""
    experience_explanation: str = ""
    skills_you_will_build: List[str] = []
    skills_you_may_miss: List[str] = []
    long_term_impact: str = ""
    key_concerns: List[str] = []
    good_for: str = ""
    avoid_if: str = ""
    reasoning: str = ""
    what_to_do_instead: str = ""


class QuickPassResult(BaseModel):
    """Result from the quick pass analysis (internal use)."""
    # Company info
    company_name: Optional[str]
    company_type: str
    company_tier: str
    
    # Basic analysis
    advertised_ctc: Optional[str]
    risk_signals_detected: List[str]
    risk_trigger: bool
    
    # AI-powered insights
    resume_guidance: dict
    candidate_insights: CandidateInsights
    risk_assessment: RiskAssessment
    
    # LLM-generated explanations
    llm_explanations: LLMExplanations
    
    # Confidence scoring
    confidence_score: float
    confidence_breakdown: ConfidenceBreakdown
    
    # Final verdict
    final_verdict: str
    
    # Meta
    analysis_source: str

