import re
from typing import Optional

def extract_ctc(jd_text: str) -> Optional[str]:
    """
    Extracts advertised CTC if present.
    Many FAANG JDs do NOT mention CTC (this is normal).
    """

    pattern = r"(\d+(\.\d+)?\s*(lpa|lakhs?|ctc))"
    match = re.search(pattern, jd_text.lower())

    if match:
        return match.group(1)

    return None
