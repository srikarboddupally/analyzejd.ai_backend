// TypeScript interfaces matching the backend FinalAnalysisResponse schema

export interface Company {
    name: string;
    type: "Product" | "Service" | "Startup" | "Captive" | "Unknown";
    context: string;
}

export interface Understanding {
    company: Company;
    role_reality: string;
}

export interface ExperienceFit {
    required_experience: string;
    fresher_alignment: "Good" | "Poor" | "Not Applicable";
    explanation: string;
}

export interface CareerImplications {
    skills_you_will_build: string[];
    skills_you_may_miss: string[];
    long_term_impact: string;
}

export interface RiskAndTradeoffs {
    risk_level: "Low" | "Medium" | "High";
    key_concerns: string[];
    good_for: string;
    avoid_if: string;
}

export interface DecisionGuidance {
    recommendation: "Apply" | "Apply with Caution" | "Skip";
    reasoning: string;
    what_to_do_instead: string;
}

export interface ResumeGuidance {
    ats_optimized_bullets: string[];
}

export interface Confidence {
    overall_confidence: number;
}

export interface AnalysisResult {
    id?: string;
    understanding: Understanding;
    experience_fit: ExperienceFit;
    career_implications: CareerImplications;
    risk_and_tradeoffs: RiskAndTradeoffs;
    decision_guidance: DecisionGuidance;
    resume_guidance: ResumeGuidance;
    confidence: Confidence;
}
