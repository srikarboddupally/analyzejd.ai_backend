"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { analyzeJD } from "@/lib/api";
import { AnalysisResult } from "@/lib/types";

export default function Home() {
  const [jdText, setJdText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (jdText.length < 50) {
      setError("Please enter at least 50 characters");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const analysis = await analyzeJD(jdText);
      setResult(analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze JD");
    } finally {
      setIsLoading(false);
    }
  };

  const getRecommendationClass = (rec: string) => {
    switch (rec) {
      case "Apply":
        return "rec-apply";
      case "Apply with Caution":
        return "rec-caution";
      case "Skip":
        return "rec-skip";
      default:
        return "";
    }
  };

  const getRecommendationIcon = (rec: string) => {
    switch (rec) {
      case "Apply":
        return "→";
      case "Apply with Caution":
        return "⚡";
      case "Skip":
        return "×";
      default:
        return "○";
    }
  };

  const getRiskClass = (risk: string) => {
    switch (risk) {
      case "Low":
        return "risk-low";
      case "Medium":
        return "risk-medium";
      case "High":
        return "risk-high";
      default:
        return "bg-muted";
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const copyBullets = () => {
    if (result) {
      const text = result.resume_guidance.ats_optimized_bullets
        .map((b) => `• ${b}`)
        .join("\n");
      copyToClipboard(text);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto flex h-14 items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <span className="font-nothing text-xl tracking-tight">⬡</span>
            <h1 className="font-nothing text-sm tracking-widest uppercase">
              AnalyzeJD
            </h1>
          </div>
          <p className="font-nothing text-xs text-muted-foreground tracking-wide hidden sm:block">
            JD Analysis for Indian Tech Engineers
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Input Section */}
        <section className="mb-12">
          <div className="mb-4">
            <span className="section-number">// input</span>
          </div>
          <Card className="nothing-card">
            <CardContent className="p-0 space-y-4">
              <Textarea
                placeholder="Paste the job description here..."
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                className="min-h-[180px] resize-y border-0 bg-transparent font-nothing text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
              />
              <div className="flex items-center justify-between pt-4 border-t border-border">
                <span className="font-nothing text-xs text-muted-foreground">
                  {jdText.length} chars
                </span>
                <Button
                  onClick={handleAnalyze}
                  disabled={isLoading || jdText.length < 50}
                  className="font-nothing text-xs tracking-wider uppercase h-9 px-6"
                >
                  {isLoading ? (
                    <span className="nothing-pulse">Processing...</span>
                  ) : (
                    <>Analyze</>
                  )}
                </Button>
              </div>
              {error && (
                <p className="font-nothing text-xs text-destructive">{error}</p>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Results Section */}
        {result && (
          <div className="space-y-8 animate-in fade-in duration-500">
            {/* 01 - Verdict */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "100ms" }}>
              <div className="mb-4">
                <span className="section-number">01 // verdict</span>
              </div>
              <Card
                className={`nothing-card ${getRecommendationClass(
                  result.decision_guidance.recommendation
                )}`}
              >
                <CardContent className="p-0">
                  <div className="flex items-start gap-4">
                    <span className="font-nothing text-4xl leading-none opacity-80">
                      {getRecommendationIcon(
                        result.decision_guidance.recommendation
                      )}
                    </span>
                    <div className="flex-1">
                      <h2 className="font-nothing text-2xl tracking-tight mb-2">
                        {result.decision_guidance.recommendation}
                      </h2>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {result.decision_guidance.reasoning}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* 02 - Company */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "200ms" }}>
              <div className="mb-4">
                <span className="section-number">02 // company</span>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0 space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <h3 className="font-nothing text-lg tracking-tight break-words">
                      {result.understanding.company.name || "Unknown"}
                    </h3>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant="outline" className="font-nothing text-xs whitespace-nowrap">
                        {result.understanding.company.type}
                      </Badge>
                      <div
                        className={`w-2 h-2 rounded-full shrink-0 ${getRiskClass(
                          result.risk_and_tradeoffs.risk_level
                        )}`}
                      />
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed border-l-2 border-border pl-4 py-1 break-words">
                    {result.understanding.company.context}
                  </p>
                </CardContent>
              </Card>
            </section>

            {/* 03 - Role Reality */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "300ms" }}>
              <div className="mb-4">
                <span className="section-number">03 // what this role really is</span>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0">
                  <p className="text-sm leading-relaxed break-words">
                    {result.understanding.role_reality}
                  </p>
                </CardContent>
              </Card>
            </section>

            {/* 04 - Experience Fit */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "400ms" }}>
              <div className="mb-4">
                <span className="section-number">04 // experience fit</span>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0 space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider">
                        Required
                      </span>
                      <p className="text-sm mt-1 break-words">
                        {result.experience_fit.required_experience}
                      </p>
                    </div>
                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider">
                        Fresher Fit
                      </span>
                      <p className="text-sm mt-1">
                        <Badge
                          variant={
                            result.experience_fit.fresher_alignment === "Good"
                              ? "default"
                              : "outline"
                          }
                          className="font-nothing whitespace-nowrap"
                        >
                          {result.experience_fit.fresher_alignment}
                        </Badge>
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed pt-4 border-t border-border break-words">
                    {result.experience_fit.explanation}
                  </p>
                </CardContent>
              </Card>
            </section>

            {/* 05 - Career Impact */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "500ms" }}>
              <div className="mb-4">
                <span className="section-number">05 // career impact</span>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0 space-y-6">
                  <div className="flex flex-col gap-6">
                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                        <span className="text-[color:var(--nothing-green)]">+</span>
                        Skills you'll build
                      </span>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {result.career_implications.skills_you_will_build.map(
                          (skill, i) => (
                            <Badge
                              key={i}
                              variant="outline"
                              className="skill-positive font-nothing text-xs whitespace-normal h-auto text-left leading-tight py-1"
                            >
                              {skill}
                            </Badge>
                          )
                        )}
                      </div>
                    </div>
                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                        <span className="text-[color:var(--nothing-red)]">−</span>
                        Skills you may miss
                      </span>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {result.career_implications.skills_you_may_miss.map(
                          (skill, i) => (
                            <Badge
                              key={i}
                              variant="outline"
                              className="skill-negative font-nothing text-xs whitespace-normal h-auto text-left leading-tight py-1"
                            >
                              {skill}
                            </Badge>
                          )
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="pt-4 border-t border-border">
                    <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider">
                      Long-term outlook
                    </span>
                    <p className="text-sm mt-2 leading-relaxed">
                      {result.career_implications.long_term_impact}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* 06 - Risk Assessment */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "600ms" }}>
              <div className="mb-4">
                <span className="section-number">06 // risk & tradeoffs</span>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0 space-y-4">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider">
                      Risk Level
                    </span>
                    <Badge
                      className={`${getRiskClass(
                        result.risk_and_tradeoffs.risk_level
                      )} text-white font-nothing text-xs`}
                    >
                      {result.risk_and_tradeoffs.risk_level}
                    </Badge>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                        <span className="text-[color:var(--nothing-green)]">✓</span>
                        Good for
                      </span>
                      <p className="text-sm mt-2 leading-relaxed">
                        {result.risk_and_tradeoffs.good_for}
                      </p>
                    </div>

                    <div>
                      <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                        <span className="text-[color:var(--nothing-red)]">✗</span>
                        Avoid if
                      </span>
                      <p className="text-sm mt-2 leading-relaxed">
                        {result.risk_and_tradeoffs.avoid_if}
                      </p>
                    </div>

                    {result.risk_and_tradeoffs.key_concerns.length > 0 &&
                      result.risk_and_tradeoffs.key_concerns[0] !== "No major concerns detected" && (
                        <div className="pt-4 border-t border-border">
                          <span className="font-nothing text-xs text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                            <span className="text-[color:var(--nothing-yellow)]">!</span>
                            Key concerns
                          </span>
                          <ul className="mt-2 space-y-1">
                            {result.risk_and_tradeoffs.key_concerns.map(
                              (concern, i) => (
                                <li
                                  key={i}
                                  className="text-sm text-muted-foreground flex items-start gap-2"
                                >
                                  <span className="font-nothing text-xs opacity-50">
                                    {String(i + 1).padStart(2, "0")}
                                  </span>
                                  {concern}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* 07 - What to Do */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "700ms" }}>
              <div className="mb-4">
                <span className="section-number">07 // what to do next</span>
              </div>
              <Card className="nothing-card border-l-4 border-l-[color:var(--nothing-blue)]">
                <CardContent className="p-0">
                  <p className="text-sm leading-relaxed">
                    {result.decision_guidance.what_to_do_instead}
                  </p>
                </CardContent>
              </Card>
            </section>

            {/* 08 - Resume Bullets */}
            <section className="animate-in slide-in-from-bottom-4 fade-in duration-700 fill-mode-backwards" style={{ animationDelay: "800ms" }}>
              <div className="mb-4 flex items-center justify-between">
                <span className="section-number">08 // resume bullets</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyBullets}
                  className="font-nothing text-xs h-6 px-2"
                >
                  Copy All
                </Button>
              </div>
              <Card className="nothing-card">
                <CardContent className="p-0">
                  <ul className="space-y-3">
                    {result.resume_guidance.ats_optimized_bullets.map(
                      (bullet, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-3 text-sm leading-relaxed group"
                        >
                          <span className="font-nothing text-xs text-muted-foreground shrink-0">
                            {String(i + 1).padStart(2, "0")}
                          </span>
                          <span className="flex-1">{bullet}</span>
                        </li>
                      )
                    )}
                  </ul>
                </CardContent>
              </Card>
            </section>

            {/* Confidence */}
            <section className="pt-4 animate-in fade-in duration-1000 fill-mode-backwards" style={{ animationDelay: "1000ms" }}>
              <div className="flex items-center justify-between text-xs text-muted-foreground font-nothing">
                <span>Analysis Confidence</span>
                <span>
                  {Math.round(result.confidence.overall_confidence * 100)}%
                </span>
              </div>
              <div className="confidence-bar mt-2">
                <div
                  className="confidence-fill"
                  style={{
                    width: `${result.confidence.overall_confidence * 100}%`,
                  }}
                />
              </div>
            </section>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="font-nothing text-xs text-muted-foreground tracking-wider">
            Built for Indian Tech Engineers
          </p>
        </div>
      </footer>
    </div>
  );
}
