def interpret_decision(
    company_type: str,
    risks: list,
    required_experience: str
) -> dict:
    if "8-10" in required_experience and company_type == "Service":
        return {
            "recommendation": "Skip",
            "risk_level": "High",
            "reasoning": "This role targets senior professionals in service-based delivery and is misaligned for freshers or early-career engineers.",
            "what_to_do_instead": "Focus on product companies or startups with explicit core engineering roles."
        }

    if company_type == "Service" and risks:
        return {
            "recommendation": "Apply with Caution",
            "risk_level": "Medium",
            "reasoning": "Service-based roles often involve limited ownership and slower technical growth.",
            "what_to_do_instead": "Apply selectively and prioritize product-focused teams."
        }

    return {
        "recommendation": "Apply",
        "risk_level": "Low",
        "reasoning": "This role aligns well with early-career engineering growth.",
        "what_to_do_instead": "Prepare strong fundamentals and project-based resume."
    }
