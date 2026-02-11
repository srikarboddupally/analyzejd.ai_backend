# app/services/pass1_quick.py
"""
Quick pass analysis using OpenAI for comprehensive JD insights.
Single API call design for cost efficiency.
"""

from typing import Optional, Tuple
from app.schemas import (
    QuickPassResult, 
    CandidateInsights, 
    RiskAssessment,
    ConfidenceBreakdown,
    LLMExplanations
)
from app.utils.text_signals import detect_risk_signals
from app.utils.company_extractor import extract_company_name, override_company_classification
from app.utils.ctc_extractor import extract_ctc
from app.ai.openai_client import analyze_jd_with_openai


# Tier scores for confidence calculation
TIER_SCORES = {
    "FAANGM": 1.0,
    "Tier-1": 0.85,
    "Tier-2": 0.65,
    "Tier-3": 0.5,
    "Unknown": 0.4
}

COMPANY_TYPE_SCORES = {
    "Product": 1.0,
    "Service": 0.75,
    "Startup": 0.7,
    "Captive": 0.65,
    "Unknown": 0.3
}


def calculate_confidence_score(
    company_name: Optional[str],
    company_type: str,
    company_tier: str,
    risk_signals: list,
    role_clarity: float
) -> Tuple[float, ConfidenceBreakdown]:
    """
    Calculate confidence score using weighted formula:
    - Company recognition: 25%
    - Risk signals: 30% 
    - Role clarity: 25%
    - Company tier: 20%
    """
    
    # Component scores
    company_recognition = 1.0 if company_name else 0.3
    
    # Risk signals: start at 1.0, deduct 0.15 per risk, min 0.2
    risk_score = max(0.2, 1.0 - (len(risk_signals) * 0.15))
    
    # Role clarity from AI analysis (0-1)
    role_clarity_score = min(1.0, max(0.0, role_clarity))
    
    # Company tier score
    tier_score = TIER_SCORES.get(company_tier, 0.4)
    
    # Weighted calculation
    confidence = (
        company_recognition * 0.25 +
        risk_score * 0.30 +
        role_clarity_score * 0.25 +
        tier_score * 0.20
    )
    
    breakdown = ConfidenceBreakdown(
        company_recognition=round(company_recognition, 2),
        risk_signals=round(risk_score, 2),
        role_clarity=round(role_clarity_score, 2),
        company_tier=round(tier_score, 2)
    )
    
    return round(confidence, 2), breakdown


def generate_final_verdict(
    confidence_score: float,
    company_name: Optional[str],
    company_tier: str,
    risk_signals: list,
    candidate_insights: dict
) -> str:
    """
    Generate human-readable verdict based on confidence score and analysis.
    """
    
    company_display = company_name or "this company"
    
    if confidence_score >= 0.8:
        verdict = f"✅ Strong opportunity at {company_display}. "
        if company_tier in ["FAANGM", "Tier-1"]:
            verdict += f"This {company_tier} company offers solid career growth. "
        verdict += "The role is well-defined with clear expectations. Worth applying with a tailored resume."
        
    elif confidence_score >= 0.6:
        verdict = f"⚠️ Proceed with caution for {company_display}. "
        if risk_signals:
            verdict += f"Noted concerns: {', '.join(risk_signals[:2])}. "
        verdict += "Research the team culture during interviews. Ask specific questions about growth paths and expectations."
        
    else:
        verdict = f"🚨 Multiple concerns detected for {company_display}. "
        if risk_signals:
            verdict += f"Red flags: {', '.join(risk_signals[:3])}. "
        verdict += "Consider carefully before applying. The role may have unclear expectations or limited growth potential."
    
    # Add candidate insight wisdom
    if candidate_insights.get("what_they_discover"):
        wisdom = candidate_insights["what_they_discover"]
        if len(wisdom) > 100:
            wisdom = wisdom[:100] + "..."
        verdict += f"\n\n💡 Insider perspective: {wisdom}"
    
    return verdict


def run_quick_pass(jd_text: str) -> QuickPassResult:
    """
    Main analysis function - combines local detection with AI insights.
    """
    
    # 1️⃣ Local extraction (fast, no API)
    risk_signals = detect_risk_signals(jd_text)
    company_name = extract_company_name(jd_text)
    ctc = extract_ctc(jd_text)
    
    # 2️⃣ AI-powered analysis (single API call)
    ai_analysis = analyze_jd_with_openai(jd_text, company_name)
    
    # 3️⃣ Extract AI results
    understanding = ai_analysis.get("understanding", {})  # Extract understanding first
    llm_company_name = understanding.get("company", {}).get("name", "")
    
    # Priority: Trust LLM extraction first (it understands context better than regex)
    if llm_company_name and llm_company_name.lower() != "unknown":
        company_name = llm_company_name
    elif not company_name:
        # Fallback: If heuristic failed too, set to empty (will be Unknown later)
        company_name = ""
        
    company_class = ai_analysis.get("company_classification", {})
    role_analysis = ai_analysis.get("role_analysis", {})
    ats_bullets = ai_analysis.get("ats_optimized_bullets", [])
    insights_data = ai_analysis.get("candidate_insights", {})
    risk_data = ai_analysis.get("risk_assessment", {})
    meta = ai_analysis.get("_meta", {})
    
    # Merge AI-detected risks with local detection
    ai_red_flags = role_analysis.get("red_flags", [])
    all_risks = list(set(risk_signals + ai_red_flags))
    
    # 4️⃣ Build structured insights
    candidate_insights = CandidateInsights(
        what_they_discover=insights_data.get("what_they_discover", ""),
        growth_potential=insights_data.get("growth_potential", "Unknown"),
        work_life_balance=insights_data.get("work_life_balance", "Unknown"),
        learning_opportunities=insights_data.get("learning_opportunities", "")
    )
    
    risk_assessment = RiskAssessment(
        risk_level=risk_data.get("risk_level", "Unknown"),
        concerns=risk_data.get("concerns", []),
        positives=risk_data.get("positives", [])
    )
    
    # 4.5 Extract LLM-generated explanations
    # LLM may return either an "explanations" object OR the full output structure
    explanations_data = ai_analysis.get("explanations", {})
    
    # Also try to extract from the full output structure (LLM sometimes returns this)
    understanding = ai_analysis.get("understanding", {})
    experience_fit = ai_analysis.get("experience_fit", {})
    career_impl = ai_analysis.get("career_implications", {})
    risk_tradeoffs = ai_analysis.get("risk_and_tradeoffs", {})
    decision_guidance = ai_analysis.get("decision_guidance", {})
    
    
    llm_explanations = LLMExplanations(
        # Extract rich company context from LLM
        company_context=understanding.get("company", {}).get("context", ""),
        required_experience=experience_fit.get("required_experience", ""),
        # Try explanations first, then fall back to full structure
        role_reality=explanations_data.get("role_reality", "") or understanding.get("role_reality", ""),
        experience_explanation=explanations_data.get("experience_explanation", "") or experience_fit.get("explanation", ""),
        skills_you_will_build=explanations_data.get("skills_you_will_build", []) or career_impl.get("skills_you_will_build", []),
        skills_you_may_miss=explanations_data.get("skills_you_may_miss", []) or career_impl.get("skills_you_may_miss", []),
        long_term_impact=explanations_data.get("long_term_impact", "") or career_impl.get("long_term_impact", ""),
        key_concerns=explanations_data.get("key_concerns", []) or risk_tradeoffs.get("key_concerns", []),
        good_for=explanations_data.get("good_for", "") or risk_tradeoffs.get("good_for", ""),
        avoid_if=explanations_data.get("avoid_if", "") or risk_tradeoffs.get("avoid_if", ""),
        reasoning=explanations_data.get("reasoning", "") or decision_guidance.get("reasoning", ""),
        what_to_do_instead=explanations_data.get("what_to_do_instead", "") or decision_guidance.get("what_to_do_instead", "")
    )
    
    # 5️⃣ Calculate confidence score
    # Override LLM classification with deterministic lookup if available
    llm_company_type = company_class.get("company_type", "Unknown")
    llm_company_tier = company_class.get("tier", "Unknown")
    
    company_type, company_tier = override_company_classification(
        company_name=company_name,
        llm_type=llm_company_type,
        llm_tier=llm_company_tier
    )
    
    role_clarity = role_analysis.get("clarity_score", 0.5)
    
    confidence_score, confidence_breakdown = calculate_confidence_score(
        company_name=company_name,
        company_type=company_type,
        company_tier=company_tier,
        risk_signals=all_risks,
        role_clarity=role_clarity
    )
    
    # 6️⃣ Generate final verdict
    final_verdict = generate_final_verdict(
        confidence_score=confidence_score,
        company_name=company_name,
        company_tier=company_tier,
        risk_signals=all_risks,
        candidate_insights=insights_data
    )
    
    # 7️⃣ Build and return result
    return QuickPassResult(
        # Company info
        company_name=company_name,
        company_type=company_type,
        company_tier=company_tier,
        
        # Basic analysis
        advertised_ctc=ctc,
        risk_signals_detected=all_risks,
        risk_trigger=len(all_risks) > 0,
        
        # AI-powered insights
        resume_guidance={"ats_optimized_bullets": ats_bullets},
        candidate_insights=candidate_insights,
        risk_assessment=risk_assessment,
        
        # LLM-generated explanations
        llm_explanations=llm_explanations,
        
        # Confidence scoring
        confidence_score=confidence_score,
        confidence_breakdown=confidence_breakdown,
        
        # Final verdict
        final_verdict=final_verdict,
        
        # Meta
        analysis_source=meta.get("source", "unknown")
    )
