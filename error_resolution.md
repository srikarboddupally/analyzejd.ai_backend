
# Error Resolution Log — LLM Explanations Integration

This document describes the issues encountered while integrating LLM-generated explanations into AnalyzeJD and how they were resolved.

---

## Issue 1: Gemini API Output Structure Mismatch

**Problem:**
Our prompt asked the LLM to return data with an `explanations` object:
```json
{ "explanations": { "role_reality": "...", "reasoning": "..." } }
```

But Gemini 2.5 returned the **final output format** directly:
```json
{ "understanding": { "role_reality": "..." }, "decision_guidance": { "reasoning": "..." } }
```

**Resolution:**
Updated `pass1_quick.py` to extract explanations from **both** possible structures:

```python
understanding = ai_analysis.get("understanding", {})
decision_guidance = ai_analysis.get("decision_guidance", {})

llm_explanations = LLMExplanations(
    role_reality=explanations_data.get("role_reality", "") or understanding.get("role_reality", ""),
    reasoning=explanations_data.get("reasoning", "") or decision_guidance.get("reasoning", ""),
    ...
)
```

**Files Changed:** `pass1_quick.py` (lines 163-186)

---

## Issue 2: Gemini Response Truncation (JSON Parse Errors)

**Problem:**
Gemini 2.5-flash truncated responses mid-JSON:
```
"role_reality": "Despite the title 'Application Architect', this role is prim...
```
Caused `json.JSONDecodeError: Unterminated string`

**Resolution:**
1. Increased `maxOutputTokens` from 1500 → **4000**
2. Added `timeout=60` (was 30)

**Files Changed:** `openai_client.py` (line 112)

---

## Issue 3: Markdown Wrapping Not Cleaned Properly

**Problem:**
Gemini returned JSON wrapped in markdown code blocks that weren't fully cleaned.

**Resolution:**
Added regex extraction to find the JSON object:

```python
import re
json_match = re.search(r'\{[\s\S]*\}', raw_text)
if json_match:
    raw_text = json_match.group(0)
```

**Files Changed:** `openai_client.py` (lines 131-143)

---

## Issue 4: Rate Limiting (429 Errors)

**Problem:**
Multiple Gemini API keys hit rate limits (429 Too Many Requests).

**Resolution:**
System already had fallback templates in `pass2_deep.py`. When LLM fails:
- Decisions remain deterministic (always work)
- Explanations fall back to templates

```python
if llm.role_reality:
    role_reality = llm.role_reality  # Use LLM
else:
    role_reality = generate_role_reality(...)  # Use template
```

---

## Issue 5: Company Classification Not Overriding LLM

**Problem:**
When Gemini returned `company_type: "Unknown"` for Wipro (a known service company), deterministic rules didn't work.

**Resolution:**
Created a deterministic company database in `company_extractor.py` with 40+ companies and override function.

**Files Changed:** `company_extractor.py`, `pass1_quick.py`

---

## Data Flow Summary

```
JD TEXT → pass1_quick.py → pass2_deep.py → FINAL OUTPUT
              │                  │
              ▼                  ▼
         Gemini API         🔧 Decisions (deterministic)
         (explanations)     🤖 Explanations (LLM → template)
```

## Files Modified

| File | Change |
|------|--------|
| `openai_client.py` | Gemini API, JSON extraction, timeout/tokens |
| `pass1_quick.py` | LLM explanation extraction from both structures |
| `pass2_deep.py` | Use LLM explanations with template fallback |
| `company_extractor.py` | 40+ company database for deterministic override |
| `schemas.py` | Added `LLMExplanations` model |
| `indian_jd_analyzer.py` | Company classification rules in prompt |
