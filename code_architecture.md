# AnalyzeJD — Code Architecture Guide

This document explains every module in the `app/` folder, organized by feature area.

---

## Folder Structure

```
app/
├── main.py                 # FastAPI entry point
├── config.py                # Environment configuration
├── schemas.py              # Pydantic models (request/response)
├── ai/                     # LLM integration
│   ├── openai_client.py    # Gemini API calls (main)
│   ├── gemini_client.py    # Alternative Gemini client
│   ├── mock_llm.py         # Mock responses for testing
│   └── company_classifier.py
├── services/               # Core business logic
│   ├── pass1_quick.py      # Quick pass analysis
│   ├── pass2_deep.py       # Deep pass analysis
│   ├── decision_interpreter.py  # Deterministic decision rules
│   ├── resume_bullets.py   # ATS bullet generation
│   └── confidence.py       # Confidence scoring
├── utils/                  # Helper utilities
│   ├── company_extractor.py # Company database & classification
│   ├── text_signals.py     # Risk keyword detection
│   ├── ctc_extractor.py    # Salary extraction
│   └── company_cache.py    # Caching utilities
└── prompts/
    └── indian_jd_analyzer.py # System prompt for LLM
```

---

## Core Flow

```
POST /analyze → main.py
       │
       ▼
   pass1_quick.py (Quick Pass)
       │
       ├── Extract company name (utils/company_extractor.py)
       ├── Detect risk signals (utils/text_signals.py)
       ├── Call Gemini API (ai/openai_client.py)
       └── Override company classification if known
       │
       ▼
   pass2_deep.py (Deep Pass)
       │
       ├── Deterministic decision (decision_interpreter.py)
       ├── Use LLM explanations OR template fallback
       └── Build final response
       │
       ▼
   FinalAnalysisResponse (JSON)
```

---

## Detailed Module Breakdown

---

### `main.py` — API Entry Point

**Purpose:** FastAPI application with two endpoints.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/analyze` | POST | Analyze a job description |

**Key Code:**
```python
@app.post("/analyze")
def analyze_jd(payload: dict):
    jd_text = payload.get("job_description", "")
    quick = run_quick_pass(jd_text)    # Step 1
    deep = run_deep_pass(jd_text, quick)  # Step 2
    return deep
```

---

### `schemas.py` — Pydantic Models

**Purpose:** Define all request/response data structures.

| Schema | Purpose |
|--------|---------|
| `Company` | Company name, type, context |
| `Understanding` | Role reality explanation |
| `ExperienceFit` | Fresher alignment check |
| `CareerImplications` | Skills you'll build/miss |
| `RiskAndTradeoffs` | Risk level, who it's for |
| `DecisionGuidance` | Final recommendation |
| `ResumeGuidance` | 3 ATS-optimized bullets |
| `FinalAnalysisResponse` | Complete output |
| `QuickPassResult` | Internal pass1 result |
| `LLMExplanations` | LLM-generated text fields |

---

## Services Folder

---

### `services/pass1_quick.py` — Quick Pass Analysis

**Purpose:** First pass – extract basic info and call AI.

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `run_quick_pass(jd_text)` | Main entry point |
| `calculate_confidence_score(...)` | Weighted confidence calculation |
| `generate_final_verdict(...)` | Human-readable verdict |

**What it does:**
1. Extract company name → `company_extractor.py`
2. Detect risk signals → `text_signals.py`
3. Call Gemini API → `openai_client.py`
4. Override company type if known (deterministic)
5. Extract LLM explanations from response
6. Return `QuickPassResult`

---

### `services/pass2_deep.py` — Deep Pass Analysis

**Purpose:** Second pass – combine LLM explanations with deterministic decisions.

**Key Architecture:**
- **Decisions are DETERMINISTIC** (via `decision_interpreter.py`)
- **Explanations prefer LLM**, fallback to templates

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `run_deep_pass(jd_text, quick)` | Main entry point |
| `extract_experience_requirement(jd_text)` | Parse experience from JD |
| `determine_fresher_alignment(exp, type)` | Good/Poor/Not Applicable |
| `generate_career_implications(type, clarity)` | Skills build/miss templates |
| `generate_role_reality(jd_text, type, risks)` | Role reality templates |

**Decision Priority:**
```
LLM Explanations → Template Fallback
Deterministic Decision → Always from decision_interpreter.py
```

---

### `services/decision_interpreter.py` — Deterministic Rules

**Purpose:** Rule-based decision logic. LLM explains, but DOES NOT decide.

**Rule Priority:**

| Priority | Condition | Result |
|----------|-----------|--------|
| 1 | Senior role + Service company | **Skip** |
| 2 | Bond/payment risks | **Skip** |
| 3 | 5+ years experience required | **Skip** |
| 4 | Service + any risks | **Apply with Caution** |
| 5 | Startup + unclear role | **Apply with Caution** |
| 6 | Service (no risks) | **Apply with Caution** |
| 7 | Product company | **Apply** |
| 8 | Captive center | **Apply** |
| 9 | Default | **Apply** |

**Why Deterministic?**
- Debuggable and predictable
- LLM can hallucinate decisions
- Rules can be audited and tested

---

### `services/resume_bullets.py` — ATS Bullet Generator

**Purpose:** Generate 3 resume bullets based on role type.

**Role Detection:**
```python
is_backend = "api" in jd or "microservices" in jd
is_frontend = "react" in jd or "angular" in jd
is_fullstack = "full stack" in jd
is_data = "data" in jd or "ml" in jd
is_devops = "aws" in jd or "kubernetes" in jd
is_qa = "testing" in jd or "qa" in jd
```

**Output:** Always exactly 3 bullets tailored to role type.

---

## AI Folder

---

### `ai/openai_client.py` — Gemini API Integration

**Purpose:** Single API call to generate explanations.

> ⚠️ Named `openai_client.py` for compatibility, but uses **Gemini API**.

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `analyze_jd_with_openai(jd_text, company)` | Main API call |
| `_build_analysis_prompt(jd_text, company)` | Build prompt |
| `_get_mock_analysis(company)` | Mock for testing |
| `_get_fallback_analysis(company, reason)` | Fallback on error |

**Configuration:**
```python
USE_MOCK_MODE = False  # Live API calls
OPENAI_MODEL = "gemini-2.5-flash"
maxOutputTokens = 4000
timeout = 60 seconds
```

**Error Handling:**
- JSON parse error → fallback
- 429 rate limit → fallback
- Network error → fallback

---

## Utils Folder

---

### `utils/company_extractor.py` — Company Database

**Purpose:** Deterministic company classification that overrides LLM.

**Database:** 40+ companies with aliases:
```python
COMPANY_DATABASE = {
    "wipro": {"type": "Service", "tier": "Tier-1"},
    "google": {"type": "Product", "tier": "FAANGM"},
    "flipkart": {"type": "Product", "tier": "Tier-1"},
    "jp morgan": {"type": "Captive", "tier": "Tier-1"},
    ...
}
```

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `extract_company_name(jd_text)` | Find company in JD |
| `get_company_classification(name)` | Lookup in database |
| `override_company_classification(name, llm_type, llm_tier)` | Override LLM if known |

---

### `utils/text_signals.py` — Risk Detection

**Purpose:** Detect red flag keywords in job descriptions.

**Risk Categories:**
```python
RISK_KEYWORDS = {
    "bond": ["bond", "service agreement", "liquidated damages"],
    "payment_risk": ["cheque", "bank guarantee", "training cost"],
    "workload": ["rotational shifts", "night shift", "6 days"]
}
```

**Function:**
```python
detect_risk_signals(text) → ["bond", "night shift", ...]
```

---

## Prompts Folder

---

### `prompts/indian_jd_analyzer.py` — System Prompt

**Purpose:** Define the LLM's persona and behavior.

**Core Principles:**
1. **Relief** → "I'm not dumb. The system is unclear."
2. **Clarity** → "Now I understand what this role really is."
3. **Confidence** → "I know how to act next."

**India-Specific Context:**
- Service companies use inflated titles
- CTC ≠ in-hand salary
- QA/testing often labeled as "engineering"
- Mass hiring funnels differ from advertised roles

**Company Classification Rules:**
- SERVICE: TCS, Infosys, Wipro, HCL, Tech Mahindra...
- PRODUCT: Google, Microsoft, Amazon, Flipkart...
- CAPTIVE: JP Morgan, Goldman Sachs, Deutsche Bank...
- STARTUP: Early-stage companies

---

## Data Flow Summary

```
┌────────────────────────────────────────────────────────────┐
│                     JD TEXT INPUT                           │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│              PASS 1: QUICK ANALYSIS                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. company_extractor → Extract company name          │ │
│  │ 2. text_signals → Detect risk keywords               │ │
│  │ 3. openai_client → Call Gemini API                   │ │
│  │ 4. Override company type if known                    │ │
│  │ 5. Extract LLM explanations                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                   Output: QuickPassResult                   │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│              PASS 2: DEEP ANALYSIS                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 🔧 DETERMINISTIC (always reliable):                  │ │
│  │    • recommendation: Apply/Skip/Caution              │ │
│  │    • risk_level: High/Medium/Low                     │ │
│  │    • fresher_alignment: Good/Poor                    │ │
│  │                                                       │ │
│  │ 🤖 LLM-GENERATED (with template fallback):           │ │
│  │    • role_reality                                     │ │
│  │    • skills_you_will_build/miss                      │ │
│  │    • reasoning, what_to_do_instead                   │ │
│  │    • good_for, avoid_if                              │ │
│  └──────────────────────────────────────────────────────┘ │
│                 Output: FinalAnalysisResponse              │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────┐
│                      JSON RESPONSE                          │
│  {                                                          │
│    "understanding": { ... },                                │
│    "experience_fit": { ... },                               │
│    "career_implications": { ... },                          │
│    "risk_and_tradeoffs": { ... },                           │
│    "decision_guidance": { ... },                            │
│    "resume_guidance": { ... },                              │
│    "confidence": { ... }                                    │
│  }                                                          │
└────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Deterministic decisions | LLMs can hallucinate; rules are debuggable |
| Company database override | Known companies should have reliable classification |
| Two-pass architecture | Quick extraction + deep analysis separation |
| Template fallbacks | System works even if API fails |
| Single API call | Cost efficiency (~$0.002 per analysis) |
| India-specific prompts | Target audience needs localized context |
