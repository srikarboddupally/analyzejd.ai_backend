import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AnalyzeJD - AI Job Description Analyzer",
  description: "AI-powered job description analyzer for Indian tech freshers and early-career engineers. Get clarity on roles, understand risks, and make confident career decisions.",
  keywords: ["job description", "JD analyzer", "career advice", "fresher jobs", "India tech"],
  openGraph: {
    title: "AnalyzeJD - AI Job Description Analyzer",
    description: "Get clarity on job descriptions. Understand what roles really mean.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
