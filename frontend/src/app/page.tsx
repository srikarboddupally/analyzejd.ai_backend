"use client";

import { useState } from "react";
import { analyzeJD } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";

export default function Home() {
  const [jdText, setJdText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleAnalyze = async () => {
    if (jdText.length < 50) {
      setError("min 50 characters");
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const analysis = await analyzeJD(jdText);
      setResult(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "analysis failed");
    } finally {
      setIsLoading(false);
    }
  };

  const verdictClass = (rec: string) => {
    if (rec === "Apply") return "verdict-apply";
    if (rec === "Apply with Caution") return "verdict-caution";
    return "verdict-skip";
  };

  const riskDot = (risk: string) => {
    if (risk === "Low") return "dot-green";
    if (risk === "Medium") return "dot-yellow";
    return "dot-red";
  };

  const copyBullets = () => {
    if (!result) return;
    const text = result.resume_guidance.ats_optimized_bullets
      .map((b, i) => `${i + 1}. ${b}`)
      .join("\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* ─── HEADER ─── */}
      <header className="border-b border-border">
        <div className="max-w-2xl mx-auto flex items-center justify-between h-12 px-4">
          <div className="flex items-center gap-2">
            <span className="mono text-base opacity-40">⬡</span>
            <span className="mono text-xs tracking-[0.2em] uppercase">
              analyzejd
            </span>
          </div>
          <span className="label hidden sm:block">
            for indian tech engineers
          </span>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-10">
        {/* ─── INPUT ─── */}
        <section className="mb-16">
          <div className="section-idx mb-4">input</div>
          <div className="n-card">
            <textarea
              placeholder="paste job description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="w-full min-h-[160px] resize-y bg-transparent mono text-sm leading-relaxed focus:outline-none placeholder:text-[color:var(--nothing-dim)]"
            />
            <div className="flex items-center justify-between pt-3 mt-3 border-t border-border">
              <span className="label">{jdText.length} chars</span>
              <button
                onClick={handleAnalyze}
                disabled={isLoading || jdText.length < 50}
                className="mono text-xs tracking-[0.15em] uppercase px-5 py-2 bg-foreground text-background disabled:opacity-30 hover:opacity-80 transition-opacity"
              >
                {isLoading ? (
                  <span className="n-pulse">analyzing...</span>
                ) : (
                  "analyze →"
                )}
              </button>
            </div>
            {error && (
              <p className="mono text-xs mt-3" style={{ color: "var(--nothing-red)" }}>
                {error}
              </p>
            )}
          </div>
        </section>

        {/* ─── RESULTS ─── */}
        {result && (
          <div className="space-y-10 animate-in fade-in duration-500">
            {/* 01 ── VERDICT */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "100ms" }}
            >
              <div className="section-idx mb-4">01 — verdict</div>
              <div
                className={`n-card ${verdictClass(
                  result.decision_guidance.recommendation
                )}`}
              >
                <div className="flex items-baseline gap-3 mb-3">
                  <span className="mono text-xl tracking-tight">
                    {result.decision_guidance.recommendation}
                  </span>
                  <span className={riskDot(result.risk_and_tradeoffs.risk_level)} />
                </div>
                <p className="text-sm leading-relaxed opacity-70">
                  {result.decision_guidance.reasoning}
                </p>
              </div>
            </section>

            {/* 02 ── COMPANY */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "200ms" }}
            >
              <div className="section-idx mb-4">02 — company</div>
              <div className="n-card">
                <div className="flex items-baseline justify-between gap-4 mb-3">
                  <span className="mono text-base tracking-tight">
                    {result.understanding.company.name || "Unknown"}
                  </span>
                  <span className="tag">
                    {result.understanding.company.type}
                  </span>
                </div>
                <p className="text-sm leading-relaxed opacity-60 border-l border-border pl-3">
                  {result.understanding.company.context}
                </p>
              </div>
            </section>

            {/* 03 ── ROLE REALITY */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "300ms" }}
            >
              <div className="section-idx mb-4">03 — what this role really is</div>
              <div className="n-card">
                <p className="text-sm leading-relaxed">
                  {result.understanding.role_reality}
                </p>
              </div>
            </section>

            {/* 04 ── EXPERIENCE FIT */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "400ms" }}
            >
              <div className="section-idx mb-4">04 — experience fit</div>
              <div className="n-card space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="label">required</span>
                    <p className="mono text-sm mt-1">
                      {result.experience_fit.required_experience}
                    </p>
                  </div>
                  <div>
                    <span className="label">fresher fit</span>
                    <p className="mt-1">
                      <span
                        className={`tag ${result.experience_fit.fresher_alignment === "Good"
                            ? "tag-positive"
                            : "tag-negative"
                          }`}
                      >
                        {result.experience_fit.fresher_alignment}
                      </span>
                    </p>
                  </div>
                </div>
                <p className="text-sm leading-relaxed opacity-60 pt-3 border-t border-border">
                  {result.experience_fit.explanation}
                </p>
              </div>
            </section>

            {/* 05 ── CAREER IMPACT */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "500ms" }}
            >
              <div className="section-idx mb-4">05 — career impact</div>
              <div className="n-card space-y-5">
                <div>
                  <span className="label flex items-center gap-2">
                    <span style={{ color: "var(--nothing-green)" }}>+</span>
                    skills you&apos;ll build
                  </span>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {result.career_implications.skills_you_will_build.map(
                      (s, i) => (
                        <span key={i} className="tag tag-positive">
                          {s}
                        </span>
                      )
                    )}
                  </div>
                </div>
                <div>
                  <span className="label flex items-center gap-2">
                    <span style={{ color: "var(--nothing-red)" }}>−</span>
                    skills you may miss
                  </span>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {result.career_implications.skills_you_may_miss.map(
                      (s, i) => (
                        <span key={i} className="tag tag-negative">
                          {s}
                        </span>
                      )
                    )}
                  </div>
                </div>
                <div className="pt-3 border-t border-border">
                  <span className="label">long-term outlook</span>
                  <p className="text-sm leading-relaxed mt-1">
                    {result.career_implications.long_term_impact}
                  </p>
                </div>
              </div>
            </section>

            {/* 06 ── RISK & TRADEOFFS */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "600ms" }}
            >
              <div className="section-idx mb-4">06 — risk &amp; tradeoffs</div>
              <div className="n-card space-y-4">
                <div className="flex items-center gap-2">
                  <span className={riskDot(result.risk_and_tradeoffs.risk_level)} />
                  <span className="mono text-xs uppercase tracking-wider">
                    {result.risk_and_tradeoffs.risk_level} risk
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <span className="label flex items-center gap-1">
                      <span style={{ color: "var(--nothing-green)" }}>✓</span>
                      good for
                    </span>
                    <p className="text-sm mt-1 leading-relaxed">
                      {result.risk_and_tradeoffs.good_for}
                    </p>
                  </div>
                  <div>
                    <span className="label flex items-center gap-1">
                      <span style={{ color: "var(--nothing-red)" }}>✗</span>
                      avoid if
                    </span>
                    <p className="text-sm mt-1 leading-relaxed">
                      {result.risk_and_tradeoffs.avoid_if}
                    </p>
                  </div>
                </div>

                {result.risk_and_tradeoffs.key_concerns.length > 0 &&
                  result.risk_and_tradeoffs.key_concerns[0] !==
                  "No major concerns detected" && (
                    <div className="pt-3 border-t border-border">
                      <span className="label">concerns</span>
                      <ul className="mt-2 space-y-1">
                        {result.risk_and_tradeoffs.key_concerns.map((c, i) => (
                          <li
                            key={i}
                            className="flex items-start gap-2 text-sm opacity-70"
                          >
                            <span className="mono text-xs opacity-40 shrink-0">
                              {String(i + 1).padStart(2, "0")}
                            </span>
                            {c}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
              </div>
            </section>

            {/* 07 ── WHAT TO DO */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "700ms" }}
            >
              <div className="section-idx mb-4">07 — what to do next</div>
              <div
                className="n-card"
                style={{ borderLeft: "3px solid var(--nothing-blue)" }}
              >
                <p className="text-sm leading-relaxed">
                  {result.decision_guidance.what_to_do_instead}
                </p>
              </div>
            </section>

            {/* 08 ── RESUME BULLETS */}
            <section
              className="animate-in slide-in-from-bottom-2 fade-in duration-500 fill-mode-backwards"
              style={{ animationDelay: "800ms" }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="section-idx flex-1">08 — resume bullets</div>
                <button
                  onClick={copyBullets}
                  className="mono text-[0.6rem] tracking-[0.15em] uppercase opacity-40 hover:opacity-100 transition-opacity"
                >
                  {copied ? "copied ✓" : "copy"}
                </button>
              </div>
              <div className="n-card">
                <ul className="space-y-3">
                  {result.resume_guidance.ats_optimized_bullets.map((b, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm leading-relaxed">
                      <span className="mono text-xs opacity-30 shrink-0 pt-0.5">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                      <span className="flex-1">{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* ── CONFIDENCE ── */}
            <section
              className="pt-6 animate-in fade-in duration-700 fill-mode-backwards"
              style={{ animationDelay: "1000ms" }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="label">confidence</span>
                <span className="mono text-xs opacity-50">
                  {Math.round(result.confidence.overall_confidence * 100)}%
                </span>
              </div>
              <div className="conf-track">
                <div
                  className="conf-fill"
                  style={{
                    width: `${result.confidence.overall_confidence * 100}%`,
                  }}
                />
              </div>
            </section>
          </div>
        )}
      </main>

      {/* ─── FOOTER ─── */}
      <footer className="border-t border-border mt-16">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
          <span className="label">analyzejd.ai</span>
          <span className="label">built for indian tech</span>
        </div>
      </footer>
    </div>
  );
}
