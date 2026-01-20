"""
OpenAI client for JD analysis - cost-optimized single API call design.
Uses gpt-4o-mini for best cost/quality ratio (~$0.002 per JD).
NOTE: Currently using Gemini API for testing while keeping OpenAI naming.
"""

import os
import json
import requests
from app.prompts.indian_jd_analyzer import get_system_prompt

# Using Gemini API for this test (keeping OpenAI naming for consistency)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
OPENAI_MODEL = "gemini-1.5-flash"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Toggle for testing without API calls
USE_MOCK_MODE = False  # Set to True for testing without API key


def _build_analysis_prompt(jd_text: str, company_name: str) -> str:
    """
    Build prompt for LLM to generate explanations.
    Note: Decisions (recommendation, risk_level) are overridden by deterministic logic.
    LLM only generates explanations and insights.
    """
    return f"""Analyze this job description for an Indian fresher/early-career engineer.

Company: {company_name or "Unknown"}
Job Description:
{jd_text[:4000]}

Generate insights in this JSON format (no markdown, no explanation outside JSON):
{{
    "company_classification": {{
        "company_type": "Product|Service|Startup|Captive|Unknown",
        "tier": "FAANGM|Tier-1|Tier-2|Tier-3|Unknown",
        "industry": "string"
    }},
    "role_analysis": {{
        "clarity_score": 0.0-1.0,
        "seniority_level": "Entry|Mid|Senior|Lead|Principal",
        "key_skills": ["skill1", "skill2", "skill3"],
        "red_flags": ["concern1"] or []
    }},
    "explanations": {{
        "role_reality": "2-3 sentences explaining what this role ACTUALLY involves day-to-day, beyond the job title. Be specific and honest.",
        "experience_explanation": "1-2 sentences explaining why this role does or does not fit freshers/early-career engineers.",
        "skills_you_will_build": ["skill1", "skill2", "skill3"],
        "skills_you_may_miss": ["skill1", "skill2", "skill3"],
        "long_term_impact": "1-2 sentences on how this role affects future career mobility.",
        "key_concerns": ["specific concern based on this JD"] or [],
        "good_for": "One sentence describing who this role is ideal for.",
        "avoid_if": "One sentence describing who should skip this role.",
        "reasoning": "2-3 sentences explaining the recommendation in a calm, mentor-like tone.",
        "what_to_do_instead": "1-2 sentences with concrete alternative roles or company types to consider."
    }},
    "ats_optimized_bullets": [
        "Achievement-focused bullet 1 using keywords from this specific JD",
        "Achievement-focused bullet 2 using keywords from this specific JD",
        "Achievement-focused bullet 3 using keywords from this specific JD"
    ],
    "candidate_insights": {{
        "what_they_discover": "What candidates typically realize AFTER joining similar roles - unwritten expectations, culture realities",
        "growth_potential": "High|Medium|Low",
        "work_life_balance": "Good|Moderate|Demanding",
        "learning_opportunities": "1-2 sentences on learning and growth paths"
    }},
    "risk_assessment": {{
        "risk_level": "Low|Medium|High",
        "concerns": ["concern1"] or [],
        "positives": ["positive1", "positive2"]
    }}
}}
"""


def analyze_jd_with_openai(jd_text: str, company_name: str) -> dict:
    """
    Single API call to analyze entire JD.
    Returns structured analysis or mock data if in mock mode.
    NOTE: Currently using Gemini API while keeping OpenAI function name.
    """
    
    if USE_MOCK_MODE:
        return _get_mock_analysis(company_name)
    
    if not OPENAI_API_KEY:
        return _get_fallback_analysis(company_name, "no_api_key")
    
    try:
        # Build the full prompt combining system + user prompts
        full_prompt = f"""{get_system_prompt()}

---
Now analyze this job description:

Company: {company_name or "Unknown"}
Job Description:
{jd_text[:3000]}

Respond with ONLY valid JSON matching the schema above.
"""
        
        # Call Gemini API
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 4000
            }
        }
        
        response = requests.post(
            f"{GEMINI_URL}?key={OPENAI_API_KEY}",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        resp_json = response.json()
        raw_text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
        
        # Save raw response for debugging
        with open("last_gemini_response.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
        
        # Clean up markdown if present - use regex to extract JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if json_match:
            raw_text = json_match.group(0)
        else:
            # Fallback: try manual cleanup
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
        
        try:
            result = json.loads(raw_text)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw text (first 1000 chars): {raw_text[:1000]}")
            return _get_fallback_analysis(company_name, f"json_parse_error")
        
        result["_meta"] = {"source": "gemini", "model": OPENAI_MODEL}
        return result
        
    except Exception as e:
        import traceback
        print(f"API Error: {e}")
        traceback.print_exc()
        return _get_fallback_analysis(company_name, f"error:{type(e).__name__}")


def _get_mock_analysis(company_name: str) -> dict:
    """Mock data for testing without API calls."""
    
    # Company-specific mock data
    company_data = {
        "meta": {
            "type": "Product", "tier": "FAANGM",
            "insights": "Candidates discover intense performance culture with high expectations. Excellent compensation but work-life balance varies by team. Strong learning opportunities but promotion cycles can be political.",
            "growth": "High", "wlb": "Demanding"
        },
        "wipro": {
            "type": "Service", "tier": "Tier-1",
            "insights": "Candidates discover client-dependent work variety. Onsite opportunities available but bench periods common. Good for building breadth of experience, less depth in cutting-edge tech.",
            "growth": "Medium", "wlb": "Moderate"
        },
        "google": {
            "type": "Product", "tier": "FAANGM",
            "insights": "Candidates discover collaborative culture with smart colleagues. Projects can feel slow due to scale. Great perks but impact visibility varies. Strong engineering culture.",
            "growth": "High", "wlb": "Good"
        },
        "tcs": {
            "type": "Service", "tier": "Tier-1",
            "insights": "Candidates discover structured career paths with good job security. Work varies by project allocation. Training opportunities available but technology exposure depends on client projects.",
            "growth": "Medium", "wlb": "Good"
        },
        "infosys": {
            "type": "Service", "tier": "Tier-1",
            "insights": "Candidates discover campus-like culture with strong training programs. Career growth possible but requires proactive networking. Work variety depends on business unit.",
            "growth": "Medium", "wlb": "Good"
        }
    }
    
    company_lower = (company_name or "").lower()
    data = company_data.get(company_lower, {
        "type": "Unknown", "tier": "Unknown",
        "insights": "Limited public information available. Research the company culture through LinkedIn connections and interview conversations.",
        "growth": "Medium", "wlb": "Moderate"
    })
    
    return {
        "company_classification": {
            "company_type": data["type"],
            "tier": data["tier"],
            "industry": "Technology"
        },
        "role_analysis": {
            "clarity_score": 0.75,
            "seniority_level": "Mid",
            "key_skills": ["Problem Solving", "Communication", "Technical Skills"],
            "red_flags": []
        },
        "ats_optimized_bullets": [
            f"Developed and deployed scalable solutions aligned with {company_name or 'company'} engineering standards, improving system reliability by 25%",
            "Led cross-functional collaboration to deliver features end-to-end, reducing time-to-market by 20%",
            "Implemented automated testing pipelines increasing code coverage to 85% and reducing production incidents"
        ],
        "candidate_insights": {
            "what_they_discover": data["insights"],
            "growth_potential": data["growth"],
            "work_life_balance": data["wlb"],
            "learning_opportunities": "Varies by team and project allocation"
        },
        "risk_assessment": {
            "risk_level": "Low" if data["tier"] in ["FAANGM", "Tier-1"] else "Medium",
            "concerns": [],
            "positives": ["Established company", "Market presence"]
        },
        "_meta": {"source": "mock", "model": "mock"}
    }


def _get_fallback_analysis(company_name: str, reason: str) -> dict:
    """Fallback when API fails."""
    return {
        "company_classification": {
            "company_type": "Unknown",
            "tier": "Unknown",
            "industry": "Unknown"
        },
        "role_analysis": {
            "clarity_score": 0.5,
            "seniority_level": "Unknown",
            "key_skills": [],
            "red_flags": []
        },
        "ats_optimized_bullets": [
            "Developed software solutions following industry best practices",
            "Collaborated with teams to deliver quality products",
            "Applied problem-solving skills to technical challenges"
        ],
        "candidate_insights": {
            "what_they_discover": "Unable to analyze. Research the company independently.",
            "growth_potential": "Unknown",
            "work_life_balance": "Unknown",
            "learning_opportunities": "Unknown"
        },
        "risk_assessment": {
            "risk_level": "Unknown",
            "concerns": ["Analysis unavailable"],
            "positives": []
        },
        "_meta": {"source": reason, "model": None}
    }
