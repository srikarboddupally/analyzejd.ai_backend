# app/ai/company_classifier.py

from app.utils.company_cache import (
    get_company_from_cache,
    save_company_to_cache
)
from app.ai.gemini_client import classify_company_with_gemini

# Mock data for testing when API quota is exceeded
MOCK_COMPANIES = {
    "meta": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "google": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "amazon": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "apple": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "netflix": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "microsoft": {"company_type": "Product", "tier": "FAANGM", "confidence": 0.95},
    "infosys": {"company_type": "Service", "tier": "Tier-1", "confidence": 0.95},
    "tcs": {"company_type": "Service", "tier": "Tier-1", "confidence": 0.95},
    "wipro": {"company_type": "Service", "tier": "Tier-1", "confidence": 0.95},
}

# Set to True to use mock data instead of Gemini API
USE_MOCK_MODE = True  # Change to False when API quota resets


def classify_company(company_name: str) -> dict:
    """
    Classifies a company using cache-first strategy.
    Gemini is called only once per company.
    """

    # 1️⃣ Cache lookup
    cached = get_company_from_cache(company_name)
    if cached:
        return cached

    # 2️⃣ Mock mode for testing
    if USE_MOCK_MODE:
        mock = MOCK_COMPANIES.get(company_name.lower())
        if mock:
            result = {
                "company_name": company_name,
                "company_type": mock["company_type"],
                "tier": mock["tier"],
                "confidence": mock["confidence"],
                "source": "mock"
            }
            save_company_to_cache(company_name, result)
            return result

    # 3️⃣ Gemini classification (safe boundary)
    try:
        classification = classify_company_with_gemini(company_name)
        company_type = classification.get("company_type", "Unknown")
        tier = classification.get("tier", "Unknown")
        confidence = 0.95 if company_type != "Unknown" else 0.5
        source = "gemini"

    except Exception:
        company_type = "Unknown"
        tier = "Unknown"
        confidence = 0.0
        source = "error"

    # 4️⃣ Normalized result
    result = {
        "company_name": company_name,
        "company_type": company_type,
        "tier": tier,
        "confidence": confidence,
        "source": source
    }

    # 5️⃣ Cache forever
    save_company_to_cache(company_name, result)

    return result
