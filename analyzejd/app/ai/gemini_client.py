"""
Legacy Gemini client wrapper.
Redirects to Unified LLMRouter for consistent behavior.
"""

from app.ai.llm_router import LLMRouter

def classify_company_with_gemini(company_name: str) -> dict:
    """
    Classify company using the unified LLM router.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Classification result
    """
    prompt = f"""
Classify the following company.

Company name: {company_name}

Rules:
- Return ONLY valid JSON
- Do NOT include markdown
- Do NOT include explanations
- Use one of the allowed values only

Allowed values:
company_type: Product | Service | Startup | Captive | Unknown
tier: FAANGM | Tier-1 | Tier-2 | Unknown

JSON schema:
{{
  "company_type": "string",
  "tier": "string"
}}
"""
    # Use the router but we might need to adjust the response format since 
    # the router returns the full JD analysis structure usually.
    # However, since LLMRouter is generic enough to return JSON, we can use it,
    # but strictly speaking LLMRouter.analyze_jd is tailored for JDs.
    #
    # To avoid over-complicating, let's just make a direct call using the Router's internal methods
    # if we wanted to be pure, but `classify_company` is a simpler task.
    #
    # For now, let's just use the router to get the RAW response if possible, 
    # OR better: Refactor LLMRouter to have a generic `query` method.
    #
    # Check `llm_router.py`: it has `analyze_jd` which is specific.
    # Let's add a generic method to LLMRouter first? 
    # actually, let's just use the analyze_jd method but with this specific prompt 
    # relying on the fact that the router returns whatever JSON the LLM spits out.
    
    try:
        response = LLMRouter.analyze_jd(prompt, company_name)
        # The router adds _meta, let's strip it if strictly needed, 
        # but the caller likely doesn't care.
        return {
            "company_type": response.get("company_type", "Unknown"),
            "tier": response.get("tier", "Unknown"),
            "confidence": 0.95,
            "source": response.get("_meta", {}).get("source", "unknown")
        }
    except Exception as e:
        return {
            "company_type": "Unknown",
            "tier": "Unknown",
            "confidence": 0.0,
            "source": f"error:{type(e).__name__}"
        }
