import os
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def _build_prompt(company_name: str) -> str:
    return f"""
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


def classify_company_with_gemini(company_name: str) -> dict:
    if not GEMINI_API_KEY:
        return {
            "company_type": "Unknown",
            "tier": "Unknown",
            "confidence": 0.0,
            "source": "no_api_key"
        }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _build_prompt(company_name)}
                ]
            }
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            json=payload,
            timeout=15
        )
        response.raise_for_status()

        resp_json = response.json()
        raw_text = resp_json["candidates"][0]["content"]["parts"][0]["text"]

        parsed = json.loads(raw_text)

        return {
            "company_type": parsed.get("company_type", "Unknown"),
            "tier": parsed.get("tier", "Unknown"),
            "confidence": 0.95,
            "source": "gemini"
        }

    except Exception as e:
        return {
            "company_type": "Unknown",
            "tier": "Unknown",
            "confidence": 0.0,
            "source": f"error:{type(e).__name__}"
        }
