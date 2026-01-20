RISK_KEYWORDS = {
    "bond": ["bond", "service agreement", "liquidated damages"],
    "payment_risk": ["cheque", "bank guarantee", "training cost"],
    "workload": ["rotational shifts", "night shift", "6 days"]
}

def detect_risk_signals(text: str):
    found = []
    lower = text.lower()
    for group in RISK_KEYWORDS.values():
        for kw in group:
            if kw in lower:
                found.append(kw)
    return list(set(found))
