# app/services/decision_interpreter.py
"""
Deterministic decision logic for JD analysis.

This module contains rule-based logic for making final recommendations.
All decisions are deterministic and debuggable - the LLM explains, but does not decide.
"""


def interpret_decision(
    company_type: str,
    risks: list,
    required_experience: str
) -> dict:
    """
    Interpret the final recommendation based on deterministic rules.
    
    Rules are applied in priority order:
    1. Senior role in service company → Skip
    2. Bond or payment risks → Skip or High Caution
    3. Service company with any risks → Apply with Caution
    4. Senior role (any company) for freshers → Skip
    5. Startup with unclear role → Apply with Caution
    6. Product company, fresher-aligned → Apply
    7. Default → Apply
    
    Returns:
        dict with recommendation, risk_level, reasoning, what_to_do_instead
    """
    
    # Normalize inputs
    exp_lower = required_experience.lower() if required_experience else ""
    risks_lower = [r.lower() for r in risks] if risks else []
    
    # --- High severity rules (Skip) ---
    
    # Rule 1: Senior role in service company
    if ("8+" in exp_lower or "8-10" in exp_lower or "lead" in exp_lower or "principal" in exp_lower):
        if company_type == "Service":
            return {
                "recommendation": "Skip",
                "risk_level": "High",
                "reasoning": (
                    "This role targets senior professionals in service-based delivery. "
                    "As a fresher or early-career engineer, you would be competing against "
                    "candidates with 8+ years of experience. Look for roles explicitly "
                    "designed for your experience level."
                ),
                "what_to_do_instead": (
                    "Focus on fresher programs at product companies, or entry-level roles "
                    "at startups where you can grow with the company."
                )
            }
    
    # Rule 2: Bond or payment-related risks
    bond_risks = any(kw in " ".join(risks_lower) for kw in ["bond", "service agreement", "liquidated damages"])
    payment_risks = any(kw in " ".join(risks_lower) for kw in ["cheque", "bank guarantee", "training cost"])
    
    if bond_risks or payment_risks:
        return {
            "recommendation": "Skip",
            "risk_level": "High",
            "reasoning": (
                "This role has concerning terms around bonds or upfront payments. "
                "Legitimate companies do not ask for financial commitments from candidates. "
                "Even if the company is genuine, bonds limit your career mobility significantly."
            ),
            "what_to_do_instead": (
                "Look for companies that invest in retention through good work culture "
                "and growth opportunities, not legal bindings."
            )
        }
    
    # Rule 3: Senior role for freshers (any company type)
    if ("5-8" in exp_lower or "5+" in exp_lower or "senior" in exp_lower):
        return {
            "recommendation": "Skip",
            "risk_level": "High",
            "reasoning": (
                "This role requires 5+ years of experience. Applying as a fresher "
                "is unlikely to succeed and may waste your time and energy. Focus on "
                "roles that match your current experience level."
            ),
            "what_to_do_instead": (
                "Apply to entry-level or associate positions. Build experience for "
                "2-3 years before targeting senior roles."
            )
        }
    
    # --- Medium severity rules (Apply with Caution) ---
    
    # Rule 4: Service company with any risks
    if company_type == "Service" and risks:
        return {
            "recommendation": "Apply with Caution",
            "risk_level": "Medium",
            "reasoning": (
                "Service-based roles often involve project-based work where your "
                "actual responsibilities depend on client allocation. The detected "
                "concerns suggest you should clarify the specific role and growth path "
                "before accepting an offer."
            ),
            "what_to_do_instead": (
                "During interviews, ask about: the specific project you'll join, "
                "the technology stack, and the typical career progression timeline."
            )
        }
    
    # Rule 5: Startup with unclear role or high risk signals
    if company_type == "Startup" and (risks or "unclear" in exp_lower or "not specified" in exp_lower):
        return {
            "recommendation": "Apply with Caution",
            "risk_level": "Medium",
            "reasoning": (
                "Startups can offer great learning but also carry risks like unclear roles, "
                "high workload, or instability. The job description lacks clarity on some "
                "important aspects."
            ),
            "what_to_do_instead": (
                "Research the startup's funding status, ask about runway, and clarify "
                "your specific responsibilities before joining."
            )
        }
    
    # Rule 6: Service company even without explicit risks
    if company_type == "Service":
        return {
            "recommendation": "Apply with Caution",
            "risk_level": "Medium",
            "reasoning": (
                "Service companies can provide good starting experience but may limit "
                "deep technical growth. Your work will depend on client projects, which "
                "you have limited control over."
            ),
            "what_to_do_instead": (
                "If you join, try to get into product-oriented teams or internal R&D "
                "groups within the company for better learning opportunities."
            )
        }
    
    # --- Low severity rules (Apply) ---
    
    # Rule 7: Product company with fresher-aligned experience
    if company_type == "Product":
        return {
            "recommendation": "Apply",
            "risk_level": "Low",
            "reasoning": (
                "Product companies generally offer better ownership and technical depth. "
                "This role appears to be a good fit for building strong engineering foundations."
            ),
            "what_to_do_instead": (
                "Prepare a strong resume highlighting projects and problem-solving skills. "
                "Practice system design basics and coding fundamentals for interviews."
            )
        }
    
    # Rule 8: Captive center
    if company_type == "Captive":
        return {
            "recommendation": "Apply",
            "risk_level": "Low",
            "reasoning": (
                "Captive centers of established companies often offer stability, structured "
                "work, and exposure to global practices. Good choice for work-life balance "
                "and steady growth."
            ),
            "what_to_do_instead": (
                "Prepare by understanding the parent company's domain. Highlight any "
                "relevant coursework or projects in that area."
            )
        }
    
    # Default: Apply
    return {
        "recommendation": "Apply",
        "risk_level": "Low",
        "reasoning": (
            "Based on the available information, this role appears suitable for "
            "early-career engineers. No major concerns detected."
        ),
        "what_to_do_instead": (
            "Prepare a strong resume and practice fundamentals. Research the company "
            "culture before interviews."
        )
    }
