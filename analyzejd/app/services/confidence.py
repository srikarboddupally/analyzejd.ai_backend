def calculate_confidence_scores(jd_text: str):
    score = 0
    text = jd_text.lower()

    if "bond" in text:
        score += 0.3
    if "rotational" in text:
        score += 0.2
    if "service" in text:
        score += 0.2

    return {
        "risk_assessment_confidence": round(min(score, 1.0), 2),
        "insider_insight_confidence": round(0.6 + score / 2, 2)
    }
