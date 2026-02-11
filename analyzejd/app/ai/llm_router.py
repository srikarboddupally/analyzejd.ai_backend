import os
import json
import time
import requests
import traceback
from typing import Dict, Any, Optional

# --- Configuration ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Models
GEMINI_MODEL = "gemini-2.0-flash"
GROQ_MODEL = "llama3-70b-8192"

# API URLs
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class LLMRouter:
    """
    Routes LLM requests with a fallback strategy:
    1. Gemini 2.0 Flash (Primary - via HTTP)
    2. Groq Llama 3 70B (Secondary - via SDK/HTTP)
    3. Mock Data (Fallback - Hardcoded)
    """
    
    @staticmethod
    def analyze_jd(prompt: str, company_name: str) -> Dict[str, Any]:
        """
        Analyze a JD using the defined fallback strategy.
        """
        # 1. Try Gemini
        if GEMINI_API_KEY:
            try:
                print(f"🚀 Attempting Gemini analysis for {company_name}...")
                return LLMRouter._call_gemini(prompt)
            except Exception as e:
                print(f"⚠️ Gemini analysis failed: {e}")
                traceback.print_exc()
        else:
            print("ℹ️ No GEMINI_API_KEY found. Skipping Gemini.")

        # 2. Try Groq
        if GROQ_API_KEY:
            try:
                print(f"🚀 Attempting Groq analysis for {company_name}...")
                return LLMRouter._call_groq(prompt)
            except Exception as e:
                print(f"⚠️ Groq analysis failed: {e}")
                traceback.print_exc()
        else:
            print("ℹ️ No GROQ_API_KEY found. Skipping Groq.")

        # 3. Fallback to Mock
        print(f"⚠️ All LLMs failed. Using Mock data for {company_name}.")
        return LLMRouter._get_mock_response(company_name)

    @staticmethod
    def _call_gemini(prompt: str) -> Dict[str, Any]:
        """Call Gemini API via HTTP."""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4000}
        }
        
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        return LLMRouter._parse_json(raw_text, "gemini")

    @staticmethod
    def _call_groq(prompt: str) -> Dict[str, Any]:
        """Call Groq API using requests (to avoid extra deps if possible, or use SDK)."""
        # Using requests for Groq to keep dependencies minimal, 
        # but 'groq' pip package is also fine. Let's use requests for consistency.
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": GROQ_MODEL,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"]
        
        return LLMRouter._parse_json(raw_text, "groq")

    @staticmethod
    def _parse_json(raw_text: str, source: str) -> Dict[str, Any]:
        """Clean and parse JSON from LLM response."""
        # 1. Strip code fences
        clean_text = raw_text
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0]
            
        clean_text = clean_text.strip()
        
        # 2. Parse
        try:
            data = json.loads(clean_text)
            data["_meta"] = {"source": source, "timestamp": time.time()}
            return data
        except json.JSONDecodeError:
            print(f"❌ JSON Parse Error from {source}. Content: {clean_text[:100]}...")
            raise

    @staticmethod
    def _get_mock_response(company_name: str) -> Dict[str, Any]:
        """Return a safe mock response."""
        return {
            "company_classification": {
                "company_type": "Unknown",
                "tier": "Unknown",
                "industry": "Technology"
            },
            "role_analysis": {
                "clarity_score": 0.5,
                "seniority_level": "Entry",
                "key_skills": ["Java", "Python", "SQL"],
                "red_flags": []
            },
             "explanations": {
                "role_reality": "This is a placeholder analysis because our AI services are temporarily unavailable.",
                "experience_explanation": "We can't determine the exact fit right now.",
                "skills_you_will_build": ["Resilience", "Debugging"],
                "skills_you_may_miss": ["Cloud Architecture"],
                "long_term_impact": "Hard to say without more data.",
                "key_concerns": ["AI Service Outage"],
                "good_for": "Testing",
                "avoid_if": "You need real real-time insights",
                "reasoning": "System fallback triggered.",
                "what_to_do_instead": "Try again in a few minutes."
            },
            "ats_optimized_bullets": [
                "Collaborated with engineering teams to maintain high system availability during outages",
                "Implemented fallback mechanisms ensuring 100% service continuity",
                "Optimized legacy code performance by 20% through refactoring"
            ],
            "candidate_insights": {
                "what_they_discover": "System resilience is key.",
                "growth_potential": "Unknown",
                "work_life_balance": "Unknown",
                "learning_opportunities": "Handling production incidents."
            },
            "risk_assessment": {
                "risk_level": "Low",
                "concerns": ["Mock Data Used"],
                "positives": ["System stayed up"]
            },
            "_meta": {"source": "mock", "timestamp": time.time()}
        }
