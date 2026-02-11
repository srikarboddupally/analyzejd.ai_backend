import { AnalysisResult } from "./types";

const API_BASE =
    process.env.NEXT_PUBLIC_API_URL || "https://analyzejd-api.onrender.com";

export async function analyzeJD(jdText: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ job_description: jdText }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            errorData.detail || `Analysis failed (${response.status})`
        );
    }

    return response.json();
}
