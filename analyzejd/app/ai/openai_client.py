"""
Unified AI Service for JD analysis using LLMRouter.
Delegates to Gemini -> Groq -> Mock strategy.
"""

from app.ai.llm_router import LLMRouter
from app.prompts.indian_jd_analyzer import get_system_prompt

def analyze_jd_with_openai(jd_text: str, company_name: str) -> dict:
    """
    Analyze JD using the multi-LLM fallback strategy.
    
    Args:
        jd_text: The full job description text
        company_name: Name of the company
        
    Returns:
        Structured dictionary matching the schema
    """
    system_prompt = get_system_prompt()
    
    full_prompt = f"""{system_prompt}

---
Now analyze this job description:

Company: {company_name or "Unknown"}
Job Description:
{jd_text[:3500]}

Respond with ONLY valid JSON matching the schema above.
"""

    return LLMRouter.analyze_jd(full_prompt, company_name)
