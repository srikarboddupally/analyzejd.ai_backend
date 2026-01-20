"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

  const getRecommendationStyle = (rec: string) => {
    switch (rec) {
      case "Apply":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "Apply with Caution":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "Skip":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "";
    }
  };

  const getRiskStyle = (risk: string) => {
    switch (risk) {
      case "Low":
        return "bg-green-600";
      case "Medium":
        return "bg-yellow-600";
      case "High":
        return "bg-red-600";
      default:
        return "bg-gray-600";
    }
  };

  const copyBullets = () => {
    if (result) {
      const text = result.resume_guidance.ats_optimized_bullets.join("\n• ");
      navigator.clipboard.writeText("• " + text);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔍</span>
            <h1 className="text-xl font-bold">AnalyzeJD</h1>
          </div>
          <p className="text-sm text-muted-foreground hidden sm:block">
            AI-powered JD analyzer for Indian tech freshers
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Input Section */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-lg">Paste Job Description</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Paste the full job description here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              className="min-h-[200px] resize-y"
            />
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {jdText.length} characters
              </span>
              <Button
                onClick={handleAnalyze}
                disabled={isLoading || jdText.length < 50}
                className="gap-2"
              >
                {isLoading ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <span>✨</span>
                    Analyze This JD
                  </>
                )}
              </Button>
            </div>
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        {result && (
          <div className="space-y-6">
            {/* Company & Recommendation */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-2xl">🏢</span>
                      <h2 className="text-xl font-semibold">
                        {result.understanding.company.name || "Unknown Company"}
                      </h2>
                      <Badge variant="secondary">
                        {result.understanding.company.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {result.understanding.company.context}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={getRiskStyle(result.risk_and_tradeoffs.risk_level)}>
                      Risk: {result.risk_and_tradeoffs.risk_level}
                    </Badge>
                  </div>
                </div>

                {/* Recommendation Banner */}
                <div
                  className={`p-4 rounded-lg border-2 ${getRecommendationStyle(
                    result.decision_guidance.recommendation
                  )}`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">
                      {result.decision_guidance.recommendation === "Apply"
                        ? "✅"
                        : result.decision_guidance.recommendation === "Skip"
                          ? "⛔"
                          : "⚠️"}
                    </span>
                    <span className="text-xl font-bold">
                      {result.decision_guidance.recommendation}
                    </span>
                  </div>
                  <p className="text-sm opacity-90">
                    {result.decision_guidance.reasoning}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Role Reality */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>🎯</span> What This Role Really Is
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  {result.understanding.role_reality}
                </p>
              </CardContent>
            </Card>

            {/* Experience Fit */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>📊</span> Experience Fit
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Required:</span>
                  <Badge variant="outline">{result.experience_fit.required_experience}</Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">Fresher Alignment:</span>
                  <Badge
                    variant={
                      result.experience_fit.fresher_alignment === "Good"
                        ? "default"
                        : "destructive"
                    }
                  >
                    {result.experience_fit.fresher_alignment}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground">
                  {result.experience_fit.explanation}
                </p>
              </CardContent>
            </Card>

            {/* Career Implications */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>📈</span> Career Impact
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid sm:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-green-500 mb-2">
                      ✅ Skills You'll Build
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.career_implications.skills_you_will_build.map(
                        (skill, i) => (
                          <Badge key={i} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-red-500 mb-2">
                      ❌ Skills You May Miss
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.career_implications.skills_you_may_miss.map(
                        (skill, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {skill}
                          </Badge>
                        )
                      )}
                    </div>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-4">
                  <strong>Long-term:</strong> {result.career_implications.long_term_impact}
                </p>
              </CardContent>
            </Card>

            {/* Risk & Tradeoffs */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <span>⚖️</span> Who Is This For?
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-green-500 mb-1">
                    ✅ Good for:
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {result.risk_and_tradeoffs.good_for}
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-red-500 mb-1">
                    ❌ Avoid if:
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {result.risk_and_tradeoffs.avoid_if}
                  </p>
                </div>
                {result.risk_and_tradeoffs.key_concerns.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-yellow-500 mb-2">
                      ⚠️ Key Concerns:
                    </h4>
                    <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                      {result.risk_and_tradeoffs.key_concerns.map((concern, i) => (
                        <li key={i}>{concern}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* What to Do Instead */}
            {result.decision_guidance.recommendation !== "Apply" && (
              <Card className="border-blue-500/30 bg-blue-500/10">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2 text-blue-400">
                    <span>💡</span> What to Do Instead
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-blue-300">
                    {result.decision_guidance.what_to_do_instead}
                  </p>
                </CardContent>
              </Card>
            )}

            {/* Resume Bullets */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span>📝</span> Resume Bullets
                  </span>
                  <Button variant="outline" size="sm" onClick={copyBullets}>
                    📋 Copy
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {result.resume_guidance.ats_optimized_bullets.map((bullet, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-3 text-sm text-muted-foreground"
                    >
                      <span className="text-primary">•</span>
                      {bullet}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {/* Confidence Score */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <span>Confidence:</span>
              <div className="w-32 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{
                    width: `${result.confidence.overall_confidence * 100}%`,
                  }}
                />
              </div>
              <span>{Math.round(result.confidence.overall_confidence * 100)}%</span>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-6 mt-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Built for Indian tech freshers 🇮🇳</p>
        </div>
      </footer>
    </div>
  );
}
