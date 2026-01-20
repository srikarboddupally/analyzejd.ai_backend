# app/services/pass2_deep.py
"""
Deep pass analysis - combines deterministic decisions with LLM explanations.

This module:
1. Uses deterministic logic for final recommendations (Apply/Caution/Skip)
2. Generates contextual explanations using company type templates
3. Produces career implications based on role patterns
"""

from app.services.decision_interpreter import interpret_decision
from app.services.resume_bullets import generate_resume_bullets
from app.schemas import (
    FinalAnalysisResponse,
    Understanding,
    Company,
    ExperienceFit,
    CareerImplications,
    RiskAndTradeoffs,
    DecisionGuidance,
    ResumeGuidance,
    Confidence
)


# --- Company Context Templates (India-specific) ---

COMPANY_CONTEXT = {
    "Product": (
        "Product companies build and sell their own software. Engineers typically work on "
        "core product features, have more ownership, and see direct impact of their work. "
        "Career growth often depends on technical depth and product impact."
    ),
    "Service": (
        "Service companies deliver projects for other businesses. Work varies by client "
        "assignment—you may work on different technologies across projects. Career growth "
        "often involves client management and broader exposure, but less depth in any single domain."
    ),
    "Startup": (
        "Startups are early-stage companies with high uncertainty but potentially high reward. "
        "Expect fast pace, broad responsibilities, and less structure. Good for learning quickly, "
        "but job security and mentorship may be limited."
    ),
    "Captive": (
        "Captive centers are offshore R&D units of foreign companies. Work is often stable "
        "and well-structured, but you may be distant from core business decisions. "
        "Good for work-life balance; growth depends on parent company culture."
    ),
    "Unknown": (
        "Unable to determine company type from the job description. Research the company "
        "independently—check LinkedIn, Glassdoor, and speak to current employees before applying."
    )
}


# --- Experience Extraction ---

def extract_experience_requirement(jd_text: str) -> str:
    """Extract experience requirement from JD text."""
    jd_lower = jd_text.lower()
    
    if "fresher" in jd_lower or "0-1" in jd_lower or "0 - 1" in jd_lower:
        return "0-1 Years (Fresher-friendly)"
    elif "1-2" in jd_lower or "1 - 2" in jd_lower or "0-2" in jd_lower:
        return "1-2 Years (Early career)"
    elif "2-4" in jd_lower or "2 - 4" in jd_lower or "3-5" in jd_lower:
        return "2-5 Years (Mid-level)"
    elif "5-8" in jd_lower or "5-7" in jd_lower or "6-8" in jd_lower:
        return "5-8 Years (Senior)"
    elif "8-10" in jd_lower or "10+" in jd_lower or "8+" in jd_lower:
        return "8+ Years (Lead/Principal)"
    else:
        return "Not explicitly specified"


def determine_fresher_alignment(required_exp: str, company_type: str) -> str:
    """Determine if role aligns well with freshers."""
    if "Fresher" in required_exp or "0-1" in required_exp or "1-2" in required_exp:
        return "Good"
    elif "2-5" in required_exp:
        return "Poor"  # Early career but not fresher
    elif "5-8" in required_exp or "8+" in required_exp or "Senior" in required_exp:
        return "Poor"
    else:
        # Unknown experience - check company type
        if company_type == "Service":
            return "Good"  # Service companies often hire freshers via mass recruitment
        return "Not Applicable"


# --- Career Implications Templates ---

def generate_career_implications(company_type: str, role_clarity: float) -> dict:
    """Generate career implications based on company type and role clarity."""
    
    implications = {
        "Product": {
            "skills_you_will_build": [
                "Deep product thinking and user empathy",
                "Ownership of features end-to-end",
                "Technical depth in specific domains"
            ],
            "skills_you_may_miss": [
                "Client-facing communication",
                "Broad technology exposure",
                "Project management across contexts"
            ],
            "long_term_impact": (
                "Strong foundation for product engineering roles. Easier transitions "
                "to other product companies or startups. May require deliberate effort "
                "to broaden technology stack."
            )
        },
        "Service": {
            "skills_you_will_build": [
                "Adaptability across different projects",
                "Client communication and requirements gathering",
                "Exposure to diverse technologies"
            ],
            "skills_you_may_miss": [
                "Deep ownership of a single product",
                "Long-term architectural decisions",
                "Direct user feedback loops"
            ],
            "long_term_impact": (
                "Broad exposure but potentially shallow depth. Transitioning to product "
                "companies later may require demonstrating depth through side projects "
                "or open source contributions."
            )
        },
        "Startup": {
            "skills_you_will_build": [
                "End-to-end ownership and scrappiness",
                "Fast learning and adaptability",
                "Wearing multiple hats (dev, ops, sometimes PM)"
            ],
            "skills_you_may_miss": [
                "Structured mentorship and code review culture",
                "Large-scale system design experience",
                "Process-driven engineering practices"
            ],
            "long_term_impact": (
                "Great for learning quickly and building a broad skill set. May need to "
                "seek structured environments later to deepen specific expertise. "
                "Startup experience is valued but stability matters too."
            )
        },
        "Captive": {
            "skills_you_will_build": [
                "Structured engineering practices",
                "Collaboration with global teams",
                "Domain expertise in parent company's area"
            ],
            "skills_you_may_miss": [
                "Product ownership and roadmap influence",
                "Startup-style scrappiness",
                "Local market understanding"
            ],
            "long_term_impact": (
                "Stable career path with good work-life balance. Growth depends on "
                "parent company's investment in the India center. May feel distant "
                "from core business decisions."
            )
        },
        "Unknown": {
            "skills_you_will_build": [
                "Unable to determine without more context"
            ],
            "skills_you_may_miss": [
                "Unable to determine without more context"
            ],
            "long_term_impact": (
                "Research the company independently before making a decision. "
                "Understanding the company type is important for career planning."
            )
        }
    }
    
    return implications.get(company_type, implications["Unknown"])


# --- Role Reality Generator ---

def generate_role_reality(jd_text: str, company_type: str, risk_signals: list) -> str:
    """Generate a plain-language explanation of what the role actually involves."""
    
    jd_lower = jd_text.lower()
    
    # Detect role patterns
    is_qa_role = any(kw in jd_lower for kw in ["qa", "quality assurance", "testing", "test automation"])
    is_support_role = any(kw in jd_lower for kw in ["support", "l1", "l2", "incident", "helpdesk"])
    is_migration_role = any(kw in jd_lower for kw in ["migration", "legacy", "modernization", "transformation"])
    is_consulting_role = any(kw in jd_lower for kw in ["consultant", "advisory", "pre-sales"])
    
    if is_qa_role:
        return (
            "This role focuses on quality assurance and testing rather than core development. "
            "Day-to-day work likely involves writing test cases, automation scripts, and "
            "coordinating with development teams. If you want to build products, this may "
            "not be the right path."
        )
    elif is_support_role:
        return (
            "This is primarily a support or operations role. Expect to handle tickets, "
            "troubleshoot issues, and work in shifts. Technical learning may be limited "
            "to the systems you support. Not ideal if you want to build new things."
        )
    elif is_migration_role:
        return (
            "This role involves migrating or maintaining existing systems rather than "
            "building new features. Work may feel repetitive and focused on legacy code. "
            "Good for stability but may limit exposure to modern architectures."
        )
    elif is_consulting_role:
        return (
            "This is a client-facing consulting role. Expect presentations, requirement "
            "gathering, and project coordination. Less hands-on coding than engineering roles. "
            "Good if you enjoy communication; less ideal for deep technical growth."
        )
    elif company_type == "Service" and risk_signals:
        return (
            "This appears to be a client-delivery role where your work depends on project "
            "allocation. Actual responsibilities may differ from what's advertised. "
            "Clarify the specific project and tech stack during interviews."
        )
    elif company_type == "Product":
        return (
            "This role involves working on the company's own product. Expect ownership "
            "of features, collaboration with product teams, and visible impact. "
            "Good environment for engineering depth and product thinking."
        )
    else:
        return (
            "Based on the job description, this appears to be a general engineering role. "
            "Clarify specific responsibilities, team structure, and projects during the "
            "interview process to understand what you'll actually be doing."
        )


# --- Main Deep Pass Function ---

def run_deep_pass(jd_text: str, quick):
    """
    Run deep analysis combining deterministic decisions with LLM explanations.
    
    Architecture:
    - DECISIONS are deterministic (recommendation, risk_level, fresher_alignment)
    - EXPLANATIONS prefer LLM-generated text, falling back to templates
    
    Args:
        jd_text: Original job description text
        quick: QuickPassResult from pass1 (includes llm_explanations)
        
    Returns:
        FinalAnalysisResponse with complete analysis
    """
    
    # Get LLM explanations (may be empty if API failed)
    llm = quick.llm_explanations
    
    # 1. Extract experience requirement (deterministic)
    required_exp = extract_experience_requirement(jd_text)
    
    # 2. Determine fresher alignment (deterministic)
    fresher_alignment = determine_fresher_alignment(required_exp, quick.company_type)
    
    # 3. Get deterministic decision (this OVERRIDES any LLM decision)
    decision = interpret_decision(
        company_type=quick.company_type,
        risks=quick.risk_signals_detected,
        required_experience=required_exp
    )
    
    # 4. Get company context (deterministic template)
    company_context = COMPANY_CONTEXT.get(quick.company_type, COMPANY_CONTEXT["Unknown"])
    
    # 5. Role reality - prefer LLM, fallback to template
    if llm.role_reality:
        role_reality = llm.role_reality
    else:
        role_reality = generate_role_reality(
            jd_text=jd_text,
            company_type=quick.company_type,
            risk_signals=quick.risk_signals_detected
        )
    
    # 6. Career implications - prefer LLM, fallback to template
    template_career = generate_career_implications(
        company_type=quick.company_type,
        role_clarity=quick.confidence_breakdown.role_clarity if hasattr(quick.confidence_breakdown, 'role_clarity') else 0.5
    )
    
    skills_build = llm.skills_you_will_build if llm.skills_you_will_build else template_career["skills_you_will_build"]
    skills_miss = llm.skills_you_may_miss if llm.skills_you_may_miss else template_career["skills_you_may_miss"]
    long_term = llm.long_term_impact if llm.long_term_impact else template_career["long_term_impact"]
    
    # 7. Fresher explanation - prefer LLM, fallback to template
    if llm.experience_explanation:
        fresher_explanation = llm.experience_explanation
    elif fresher_alignment == "Good":
        fresher_explanation = (
            "This role appears suitable for freshers or early-career engineers. "
            "The experience requirements and role type suggest a reasonable starting point."
        )
    elif fresher_alignment == "Poor":
        fresher_explanation = (
            "This role targets more experienced professionals. As a fresher, you may "
            "struggle to meet expectations or miss out on proper mentorship. Consider "
            "roles explicitly designed for early-career engineers."
        )
    else:
        fresher_explanation = (
            "The experience requirements are unclear. Research the role further and "
            "ask directly about the expected experience level during the application process."
        )
    
    # 8. Risk tradeoffs - prefer LLM, fallback to template
    if llm.good_for:
        good_for = llm.good_for
    elif quick.company_type == "Product":
        good_for = "Engineers who want deep ownership, product impact, and technical depth."
    elif quick.company_type == "Service":
        good_for = "Engineers comfortable with client work and seeking diverse project exposure."
    elif quick.company_type == "Startup":
        good_for = "Self-starters who thrive in ambiguity and want to learn fast."
    elif quick.company_type == "Captive":
        good_for = "Engineers seeking stability, global exposure, and work-life balance."
    else:
        good_for = "Unclear without more information about the company."
    
    if llm.avoid_if:
        avoid_if = llm.avoid_if
    elif quick.company_type == "Product":
        avoid_if = "You prefer variety across projects or want broad technology exposure."
    elif quick.company_type == "Service":
        avoid_if = "You want deep product ownership or dislike project-based assignments."
    elif quick.company_type == "Startup":
        avoid_if = "You need structured mentorship or job security is a priority."
    elif quick.company_type == "Captive":
        avoid_if = "You want to influence product direction or prefer fast-moving environments."
    else:
        avoid_if = "You are risk-averse and prefer clarity before committing."
    
    # 9. Key concerns - combine LLM + detected signals
    key_concerns = llm.key_concerns if llm.key_concerns else []
    if quick.risk_signals_detected:
        key_concerns = list(set(key_concerns + quick.risk_signals_detected))
    if not key_concerns:
        key_concerns = ["No major concerns detected"]
    
    # 10. Decision reasoning - prefer LLM but always use deterministic decision
    # Note: We use LLM reasoning but the recommendation itself is deterministic
    reasoning = llm.reasoning if llm.reasoning else decision["reasoning"]
    what_to_do = llm.what_to_do_instead if llm.what_to_do_instead else decision["what_to_do_instead"]
    
    # 11. Resume bullets - prefer LLM, fallback to template
    ats_bullets = quick.resume_guidance.get("ats_optimized_bullets", [])
    if not ats_bullets or len(ats_bullets) < 3:
        ats_bullets = generate_resume_bullets(jd_text)
    # Ensure exactly 3 bullets
    ats_bullets = ats_bullets[:3]
    while len(ats_bullets) < 3:
        ats_bullets.append("Developed software solutions following industry best practices")
    
    # 12. Build and return final response
    return FinalAnalysisResponse(
        understanding=Understanding(
            company=Company(
                name=quick.company_name or "Unknown",
                type=quick.company_type if quick.company_type in ["Product", "Service", "Startup", "Captive"] else "Unknown",
                context=company_context
            ),
            role_reality=role_reality
        ),
        experience_fit=ExperienceFit(
            required_experience=required_exp,
            fresher_alignment=fresher_alignment,  # DETERMINISTIC
            explanation=fresher_explanation
        ),
        career_implications=CareerImplications(
            skills_you_will_build=skills_build,
            skills_you_may_miss=skills_miss,
            long_term_impact=long_term
        ),
        risk_and_tradeoffs=RiskAndTradeoffs(
            risk_level=decision["risk_level"],  # DETERMINISTIC
            key_concerns=key_concerns,
            good_for=good_for,
            avoid_if=avoid_if
        ),
        decision_guidance=DecisionGuidance(
            recommendation=decision["recommendation"],  # DETERMINISTIC
            reasoning=reasoning,
            what_to_do_instead=what_to_do
        ),
        resume_guidance=ResumeGuidance(
            ats_optimized_bullets=ats_bullets
        ),
        confidence=Confidence(
            overall_confidence=quick.confidence_score
        )
    )

