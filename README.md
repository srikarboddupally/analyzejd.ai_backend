# AnalyzeJD.ai — System Architecture & Execution Plan

## 1. Product Goal (Single Sentence)

AnalyzeJD.ai helps candidates:
- Understand **any tech job description** clearly
- Identify **company reality and expectations**
- Detect **risk patterns when present**
- Generate **ATS-optimized resume bullets** for every JD
while minimizing token cost and avoiding hallucinations.

---

## 2. Core Design Principles

1. **Always useful output**
   - Even clean JDs (Meta, Google, Amazon) must produce value
2. **Cost-aware by default**
   - Expensive reasoning only when justified
3. **Deterministic first, LLM second**
   - Regex, heuristics, caching before model calls
4. **Advisory, not authoritative**
   - No legal or factual claims without certainty
5. **Strict schemas**
   - Predictable JSON → stable frontend

---

## 3. High-Level Architecture (Current)

Client (UI / API)
|
v
FastAPI
|
v
+---------------------------+
| Pass 1 : Always-On Layer |
+---------------------------+
| - Company detection |
| - Company classification |
| - JD understanding |
| - Risk signal detection |
| - ATS resume bullets (3) |
+---------------------------+
|
| risk_trigger OR prestige_trigger
v
+---------------------------+
| Pass 2 : Deep Insights |
+---------------------------+
| - Insider-style insights |
| - Role reality check |
| - Risk explanation |
| - Final verdict |
| - Confidence scores |
+---------------------------+

---

## 4. What Runs ALWAYS (for every JD)

### 4.1 Company Intelligence (Mandatory)
- Detect company name if possible
- Classify company type:
  - Product
  - Service
  - Startup
  - Captive
  - Unknown
- Identify Tier (FAANG / Tier-1 / Other) when known

Purpose:
> Even clean, prestigious JDs must explain *what working here typically means*.

---

### 4.2 JD Understanding (Mandatory)
Translate vague JD language into:
- Expected work
- Evaluation signals
- Skill depth required

Purpose:
> Help candidates truly understand what the JD implies.

---

### 4.3 Resume Optimization (Mandatory, Non-Conditional)
- Generate **exactly 3 ATS-optimized resume bullet points**
- Bullets must:
  - Use strong action verbs
  - Reflect JD keywords
  - Be copy-paste ready
- No explanations, no verbosity

Purpose:
> Immediate, tangible value for every user.

---

## 5. What Runs CONDITIONALLY (Cost-Controlled)

### 5.1 Risk Analysis
Triggered when:
- Bond / service agreement patterns detected
- Rotational shifts / exploitative clauses detected
- Other high-risk signals present

Output:
- Risk signals
- Advisory risk level
- Clear explanation (not legal judgment)

---

### 5.2 Insider-Style Insights
Triggered when:
- Risk signals present OR
- Company is Tier-1 / FAANG / high-signal tech company

Output:
- “What candidates often discover after joining”
- Based on **industry patterns**, not scraped content
- Clearly advisory and simulated

---

## 6. Confidence Scoring (Current State)

Each deep insight includes confidence scores:
- `risk_assessment_confidence`
- `insider_insight_confidence`

Characteristics:
- Deterministic
- Explainable
- Keyword / signal weighted
- No LLM usage

Purpose:
> Prevent overtrust and communicate uncertainty honestly.

---

## 7. Current Directory Structure

analyzejd/
├── app/
│ ├── main.py
│ ├── config.py
│ ├── schemas.py
│ ├── prompts/
│ │ └── indian_jd_analyzer.py
│ ├── services/
│ │ ├── pass1_quick.py
│ │ ├── pass2_deep.py
│ │ ├── resume_bullets.py
│ │ └── confidence.py
│ ├── ai/
│ │ ├── client.py
│ │ └── mock_llm.py
│ └── utils/
│ ├── text_signals.py
│ ├── company_extractor.py
│ └── ctc_extractor.py


---

## 8. Company Detection Strategy (Design Decision)

### Chosen Path: **Option 2 — Scalable, Still Cheap**

#### Why Option 2
- Works for **any tech company in the world**
- No hardcoded limits
- Low token usage
- Cacheable forever

#### Strategy
1. Extract probable company name (regex / heuristics)
2. Send ONLY the company name to an LLM:
   > “Classify this company by type and tier”
3. Cache the result (company → metadata)
4. Reuse forever (zero repeated cost)

This avoids:
- JD-level LLM calls
- Hallucinating from long text
- Manual company lists at scale

---

## 9. LLM Usage Roadmap

### Phase 1 (Current)
- Mock LLM
- Deterministic logic
- Zero token burn

### Phase 2 (Next)
- Implement Option 2 company classifier
- Test with **Gemini free API**
- Cache results
- Validate accuracy

### Phase 3 (Final)
- Switch classifier to OpenAI
- Strict schema enforcement
- Token measurement
- Production hardening

---

## 10. Non-Goals (Explicitly Out of Scope)

- Scraping Glassdoor / Reddit
- Quoting external reviews
- Making legal or salary guarantees
- Oververbose explanations

---

## 11. Definition of “Correct Output”

An output is correct if:
- No hallucinated facts
- Unknowns are `null`
- Clean JDs produce insights, not warnings
- Risky JDs produce caution, not panic
- Resume bullets are always present and usable

---

## 12. Current Status

✅ Architecture finalized  
✅ Resume optimization always-on  
✅ Two-pass pipeline in place  
✅ Confidence scoring implemented  
⏳ Company detection Option 2 — **NEXT**

---

## 13. Next Step (Agreed)

1. Implement **Option 2 company classification**
2. Test using **Gemini free API**
3. Cache results
4. Validate with Meta / Google / Amazon / random startups
5. Then integrate OpenAI safely



<!-- 👉 You should make this explicit in the schema later for Resume Bulletpoints mismatch(Not aligning with actual JD, generic SWE points ):

<!-- "resume_guidance": {
  "strategy": "Escape | Align",
  "ats_optimized_bullets": [...]
} -->


But for MVP? This is acceptable. -->
---

_End of architecture document._
