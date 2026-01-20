# app/utils/company_extractor.py
"""
Deterministic company extraction and classification.

This module provides reliable company detection that doesn't depend on LLM output.
Used as a fallback/override when LLM returns Unknown or incorrect classification.
"""

import re

# Company database with name aliases and classification
COMPANY_DATABASE = {
    # === FAANGM (Product, Tier: FAANGM) ===
    "meta": {
        "aliases": ["meta", "meta platforms", "facebook"],
        "type": "Product",
        "tier": "FAANGM"
    },
    "google": {
        "aliases": ["google", "alphabet", "google llc"],
        "type": "Product",
        "tier": "FAANGM"
    },
    "amazon": {
        "aliases": ["amazon", "amazon.com", "amazon india"],
        "type": "Product",
        "tier": "FAANGM"
    },
    "microsoft": {
        "aliases": ["microsoft", "microsoft india"],
        "type": "Product",
        "tier": "FAANGM"
    },
    "apple": {
        "aliases": ["apple", "apple india"],
        "type": "Product",
        "tier": "FAANGM"
    },
    "netflix": {
        "aliases": ["netflix"],
        "type": "Product",
        "tier": "FAANGM"
    },
    
    # === Semiconductor Giants (Product, Tier: FAANGM/Tier-1) ===
    "qualcomm": {
        "aliases": ["qualcomm", "qualcomm india", "qualcomm india private limited"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "intel": {
        "aliases": ["intel", "intel india", "intel corporation"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "nvidia": {
        "aliases": ["nvidia", "nvidia india", "nvidia corporation"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "amd": {
        "aliases": ["amd", "advanced micro devices"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "broadcom": {
        "aliases": ["broadcom", "broadcom india"],
        "type": "Product",
        "tier": "Tier-1"
    },
    
    # === Indian IT Services (Service, Tier: Tier-1) ===
    "wipro": {
        "aliases": ["wipro", "wipro limited", "wipro technologies"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "tcs": {
        "aliases": ["tcs", "tata consultancy services", "tata consultancy"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "infosys": {
        "aliases": ["infosys", "infosys limited", "infosys technologies"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "hcl": {
        "aliases": ["hcl", "hcl technologies", "hcltech"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "tech mahindra": {
        "aliases": ["tech mahindra", "techmahindra"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "cognizant": {
        "aliases": ["cognizant", "cognizant technology solutions", "cts"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "capgemini": {
        "aliases": ["capgemini", "cap gemini"],
        "type": "Service",
        "tier": "Tier-1"
    },
    "accenture": {
        "aliases": ["accenture", "accenture india"],
        "type": "Service",
        "tier": "Tier-1"
    },
    
    # === Indian IT Services (Service, Tier: Tier-2) ===
    "ltimindtree": {
        "aliases": ["ltimindtree", "lti", "mindtree", "l&t infotech"],
        "type": "Service",
        "tier": "Tier-2"
    },
    "mphasis": {
        "aliases": ["mphasis"],
        "type": "Service",
        "tier": "Tier-2"
    },
    "persistent": {
        "aliases": ["persistent", "persistent systems"],
        "type": "Service",
        "tier": "Tier-2"
    },
    "hexaware": {
        "aliases": ["hexaware", "hexaware technologies"],
        "type": "Service",
        "tier": "Tier-2"
    },
    "cyient": {
        "aliases": ["cyient", "cyient limited"],
        "type": "Service",
        "tier": "Tier-2"
    },
    "zensar": {
        "aliases": ["zensar", "zensar technologies"],
        "type": "Service",
        "tier": "Tier-2"
    },
    
    # === Indian Product/Unicorns (Product, Tier: Tier-1) ===
    "flipkart": {
        "aliases": ["flipkart"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "swiggy": {
        "aliases": ["swiggy"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "zomato": {
        "aliases": ["zomato"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "razorpay": {
        "aliases": ["razorpay"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "phonepe": {
        "aliases": ["phonepe", "phone pe"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "paytm": {
        "aliases": ["paytm", "one97"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "zerodha": {
        "aliases": ["zerodha"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "cred": {
        "aliases": ["cred"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "meesho": {
        "aliases": ["meesho"],
        "type": "Product",
        "tier": "Tier-1"
    },
    
    # === Captive Centers (Captive, Tier: Tier-1) ===
    "goldman sachs": {
        "aliases": ["goldman sachs", "gs", "goldman"],
        "type": "Captive",
        "tier": "Tier-1"
    },
    "jp morgan": {
        "aliases": ["jp morgan", "jpmorgan", "chase", "jpm"],
        "type": "Captive",
        "tier": "Tier-1"
    },
    "morgan stanley": {
        "aliases": ["morgan stanley"],
        "type": "Captive",
        "tier": "Tier-1"
    },
    "deutsche bank": {
        "aliases": ["deutsche bank", "db"],
        "type": "Captive",
        "tier": "Tier-1"
    },
    "barclays": {
        "aliases": ["barclays"],
        "type": "Captive",
        "tier": "Tier-1"
    },
    
    # === Global Product (Product, Tier: Tier-1) ===
    "adobe": {
        "aliases": ["adobe", "adobe systems"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "salesforce": {
        "aliases": ["salesforce"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "oracle": {
        "aliases": ["oracle"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "sap": {
        "aliases": ["sap", "sap labs"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "atlassian": {
        "aliases": ["atlassian"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "uber": {
        "aliases": ["uber"],
        "type": "Product",
        "tier": "Tier-1"
    },
    "linkedin": {
        "aliases": ["linkedin"],
        "type": "Product",
        "tier": "Tier-1"
    },
}


def extract_company_name(jd_text: str) -> str | None:
    """Extract company name from JD text using known aliases."""
    text = jd_text.lower()

    # 1. Try known companies first (high precision)
    for canonical, data in COMPANY_DATABASE.items():
        for alias in data["aliases"]:
            if re.search(rf"\b{re.escape(alias.lower())}\b", text):
                return canonical.title()

    # 2. Fallback: heuristic extraction (for unknown companies)
    patterns = [
        r"\bAbout\s+([A-Z][a-zA-Z0-9\&\-. ]+)",
        r"\b([A-Z][a-zA-Z0-9\&\-. ]+)\s+is\s+seeking\b",
        r"\bjoin\s+([A-Z][a-zA-Z0-9\&\-. ]+)",
        r"\b([A-Z][a-zA-Z0-9\&\-. ]+)\s+is\s+hiring\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, jd_text)
        if match:
            return match.group(1).strip()

    return None


def get_company_classification(company_name: str) -> dict | None:
    """
    Get deterministic classification for a known company.
    
    Returns:
        dict with 'type' and 'tier' if company is known, None otherwise
    """
    if not company_name:
        return None
    
    name_lower = company_name.lower()
    
    # Direct match
    if name_lower in COMPANY_DATABASE:
        data = COMPANY_DATABASE[name_lower]
        return {"type": data["type"], "tier": data["tier"]}
    
    # Check against aliases
    for canonical, data in COMPANY_DATABASE.items():
        for alias in data["aliases"]:
            if alias.lower() == name_lower or name_lower in alias.lower():
                return {"type": data["type"], "tier": data["tier"]}
    
    return None


def override_company_classification(
    company_name: str,
    llm_type: str,
    llm_tier: str
) -> tuple[str, str]:
    """
    Override LLM classification with deterministic lookup if available.
    
    Args:
        company_name: Extracted company name
        llm_type: Company type from LLM (may be Unknown)
        llm_tier: Company tier from LLM (may be Unknown)
    
    Returns:
        Tuple of (final_type, final_tier) - uses deterministic if available
    """
    known = get_company_classification(company_name)
    
    if known:
        # Deterministic takes priority
        return known["type"], known["tier"]
    
    # Fall back to LLM classification
    return llm_type, llm_tier
