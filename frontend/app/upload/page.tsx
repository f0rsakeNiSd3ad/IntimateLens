"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  Upload, 
  Loader2, 
  AlertCircle, 
  CheckCircle2, 
  XCircle, 
  Heart, 
  ShieldAlert, 
  FileText, 
  Sparkles,
  ArrowRight
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressRing } from "@/components/ui/progress-ring";
import { cn } from "@/lib/utils";

interface AnalysisResult {
  toxicity_score: number;
  affection_levels: { [key: string]: number; person_a: number; person_b: number };
  speaker_a?: string;
  speaker_b?: string;
  key_red_flags: string[];
  key_green_flags: string[];
  verdict: string;
  actionable_advice: string[];
  gottman_breakdown?: {
    criticism_score: number;
    contempt_score: number;
    defensiveness_score: number;
    stonewalling_score: number;
    notes?: string;
  };
  timeline_events?: Array<{
    timestamp: string;
    speaker: string;
    message?: string;
    sentiment_impact: number;
    label: string;
  }>;
  normalized_conversation?: Array<{
    original_sender: string;
    normalized_text: string;
    original_text: string;
    emotion_tone: string | null;
  }>;
  repair_blueprint?: {
    blueprint_type?: string;
    headline?: string;
    brutal_truth_summary: string;
    hopeful_path_summary: string;
    person_diagnostics?: Array<{
      name: string;
      attachment_style: string;
      primary_issues: string[];
      strengths: string[];
      action_plan: string;
    }>;
    protocols: Array<{
      title: string;
      principle: string;
      action: string;
      script: string;
      rule: string;
    }>;
  };
}

interface UploadState {
  file: File | null;
  userInstructions: string;
  loading: boolean;
  error: string | null;
  result: AnalysisResult | null;
}

export default function UploadPage() {
  const [state, setState] = useState<UploadState>({
    file: null,
    userInstructions: "",
    loading: false,
    error: null,
    result: null,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!state.file) {
      setState(prev => ({ ...prev, error: "Please select a chat file first." }));
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null, result: null }));

    const formData = new FormData();
    formData.append("file", state.file);
    formData.append("user_instructions", state.userInstructions);

    const endpoints = [
      process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/analyze` : null,
      "http://127.0.0.1:8001/analyze",
      "http://localhost:8001/analyze",
      "http://127.0.0.1:8000/analyze",
      "http://localhost:8000/analyze",
    ].filter(Boolean) as string[];

    let lastError: Error | null = null;
    let successData: AnalysisResult | null = null;

    for (const url of endpoints) {
      try {
        const response = await fetch(url, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          let errorMsg = "Analysis failed";
          let isIntimacyLensDetail = false;
          try {
            const errData = await response.json();
            if (errData && errData.detail) {
              errorMsg = errData.detail;
              isIntimacyLensDetail = true;
            }
          } catch {
            errorMsg = `Server error HTTP ${response.status}: ${response.statusText}`;
          }
          // If our backend returned a specific validation error (e.g. 400 bad format), stop retrying
          if (isIntimacyLensDetail && (response.status === 400 || response.status === 422)) {
            lastError = new Error(errorMsg);
            break;
          }
          throw new Error(errorMsg);
        }

        successData = await response.json();
        break;
      } catch (err: any) {
        lastError = err;
        // If it's a specific validation error from our backend, stop trying other endpoints
        if (err.message && !err.message.toLowerCase().includes("fetch") && !err.message.includes("403") && !err.message.includes("404")) {
          break;
        }
      }
    }

    if (successData) {
      setState(prev => ({ ...prev, loading: false, result: successData }));
      try {
        sessionStorage.setItem("latest_analysis", JSON.stringify(successData));
      } catch (e) {
        console.error("Could not save to sessionStorage", e);
      }
    } else {
      let friendlyError = lastError?.message || "An unexpected error occurred.";
      if (lastError?.message?.toLowerCase().includes("fetch") || lastError?.message?.includes("403")) {
        friendlyError = "Backend server is not reachable at http://127.0.0.1:8001. Please make sure the backend is running by executing start.bat or backend/run_server.bat.";
      }
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: friendlyError 
      }));
    }
  };

  const getToxicityColor = (score: number) => {
    if (score >= 60) return "text-destructive";
    if (score >= 35) return "text-amber-500";
    return "text-emerald-500";
  };

  const getVerdictBadge = (verdict: string) => {
    switch (verdict) {
      case "Healthy":
      case "Repairable":
        return "bg-emerald-100 text-emerald-800 border-emerald-300";
      case "Critical":
        return "bg-amber-100 text-amber-800 border-amber-300";
      case "Recommend Ending":
        return "bg-rose-100 text-rose-800 border-rose-300";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  const speakerA = state.result?.speaker_a || state.result?.normalized_conversation?.[0]?.original_sender || "Person A";
  const speakerB = state.result?.speaker_b || 
    state.result?.normalized_conversation?.find(m => m.original_sender && m.original_sender !== speakerA)?.original_sender || 
    "Person B";
  const affA = state.result ? (state.result.affection_levels[speakerA] ?? state.result.affection_levels.person_a ?? 50) : 50;
  const affB = state.result ? (state.result.affection_levels[speakerB] ?? state.result.affection_levels.person_b ?? 50) : 50;

  return (
    <div className="min-h-screen bg-background p-6 md:p-12 font-sans antialiased">
      <div className="max-w-4xl mx-auto space-y-8">

        {/* Header */}
        <header className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
            <Sparkles className="w-3.5 h-3.5" /> Privacy-First On-Device AI
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-primary via-primary/80 to-accent bg-clip-text text-transparent">
            IntimacyLens
          </h1>
          <p className="text-muted-foreground max-w-xl mx-auto text-base">
            Upload text exports from WhatsApp, Instagram, or SMS to analyze relationship dynamics, Gottman markers, and communication health.
          </p>
        </header>

        {/* Error Alert */}
        {state.error && (
          <div className="p-4 rounded-lg border border-destructive/30 bg-destructive/10 flex items-start gap-3 text-destructive">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-sm">Analysis Request Failed</h4>
              <p className="text-sm mt-0.5 opacity-90">{state.error}</p>
            </div>
          </div>
        )}

        {/* Upload Form */}
        <Card className="shadow-sm border">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary" /> Upload Conversation Export
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-1.5 text-foreground">
                  Chat File (.txt or .json)
                </label>
                <div className="border-2 border-dashed rounded-lg p-6 text-center hover:border-primary/50 transition-colors">
                  <input
                    type="file"
                    accept=".txt,.json"
                    onChange={(e) => setState(prev => ({ ...prev, file: e.target.files?.[0] || null }))}
                    className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 cursor-pointer"
                    required
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Supports WhatsApp ([DD/MM/YYYY, HH:MM] Alice: Msg), Instagram, SMS, and JSON formats.
                  </p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1 text-foreground">
                  User Context / Instructions (Optional)
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Helps the AI understand cultural dialect, slang, abbreviations, or Hinglish/Romanized text.
                </p>
                <textarea
                  value={state.userInstructions}
                  onChange={(e) => setState(prev => ({ ...prev, userInstructions: e.target.value }))}
                  placeholder="e.g., This conversation is in informal Hinglish with lots of slang and sarcasm."
                  className="w-full p-3 border rounded-md focus:ring-2 focus:ring-primary focus:border-transparent min-h-[90px] resize-y bg-background text-sm"
                  rows={3}
                ></textarea>
              </div>

              <button
                type="submit"
                disabled={state.loading}
                className={cn(
                  "w-full py-3.5 px-6 rounded-md font-medium text-base transition-all duration-200 flex items-center justify-center gap-2",
                  state.loading 
                    ? "bg-primary/60 text-primary-foreground cursor-not-allowed" 
                    : "bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm active:scale-[0.99]"
                )}
              >
                {state.loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Analyzing Conversation...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    <span>Analyze Conversation</span>
                  </>
                )}
              </button>
            </form>
          </CardContent>
        </Card>

        {/* Results Section */}
        {state.result && (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold tracking-tight">Analysis Dashboard</h2>
              <Link 
                href="/dashboard"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
              >
                Open Full Analytics <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Verdict Card */}
            <Card className="p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <span className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">
                    Relationship Diagnosis
                  </span>
                  <div className="mt-1 flex items-center gap-3">
                    <span className={cn("px-3.5 py-1 text-sm font-semibold rounded-full border", getVerdictBadge(state.result.verdict))}>
                      {state.result.verdict}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <span className="text-xs text-muted-foreground block mb-1">Toxicity</span>
                    <ProgressRing 
                      value={state.result.toxicity_score} 
                      size={64} 
                      strokeWidth={6} 
                      colorClassName={getToxicityColor(state.result.toxicity_score)}
                    />
                    <span className="text-xs font-bold block mt-1">{state.result.toxicity_score}/100</span>
                  </div>
                  <div className="text-center">
                    <span className="text-xs text-muted-foreground block mb-1 font-medium">{speakerA} Affection</span>
                    <ProgressRing 
                      value={affA} 
                      size={64} 
                      strokeWidth={6} 
                      colorClassName="text-primary"
                    />
                    <span className="text-xs font-bold block mt-1">{affA}%</span>
                  </div>
                  <div className="text-center">
                    <span className="text-xs text-muted-foreground block mb-1 font-medium">{speakerB} Affection</span>
                    <ProgressRing 
                      value={affB} 
                      size={64} 
                      strokeWidth={6} 
                      colorClassName="text-accent"
                    />
                    <span className="text-xs font-bold block mt-1">{affB}%</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Red & Green Flags */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6 border-red-200/50">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold flex items-center gap-2 text-destructive">
                    <XCircle className="w-5 h-5" /> Key Red Flags
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <ul className="space-y-2.5 text-sm">
                    {state.result.key_red_flags.map((flag, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-destructive font-bold">•</span>
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>

              <Card className="p-6 border-emerald-200/50">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold flex items-center gap-2 text-emerald-600">
                    <CheckCircle2 className="w-5 h-5" /> Key Green Flags
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <ul className="space-y-2.5 text-sm">
                    {state.result.key_green_flags.map((flag, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-600 font-bold">•</span>
                        <span>{flag}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>

            {/* Gottman Breakdown */}
            {state.result.gottman_breakdown && (
              <Card className="p-6">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-primary" /> Gottman Four Horsemen Markers
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                    <div className="p-3 bg-muted/30 rounded-lg">
                      <span className="text-xs text-muted-foreground block">Criticism</span>
                      <span className="text-2xl font-bold text-amber-500">{state.result.gottman_breakdown.criticism_score}</span>
                      <span className="text-[10px] text-muted-foreground block">/ 100</span>
                    </div>
                    <div className="p-3 bg-muted/30 rounded-lg">
                      <span className="text-xs text-muted-foreground block">Contempt</span>
                      <span className="text-2xl font-bold text-destructive">{state.result.gottman_breakdown.contempt_score}</span>
                      <span className="text-[10px] text-muted-foreground block">/ 100</span>
                    </div>
                    <div className="p-3 bg-muted/30 rounded-lg">
                      <span className="text-xs text-muted-foreground block">Defensiveness</span>
                      <span className="text-2xl font-bold text-blue-500">{state.result.gottman_breakdown.defensiveness_score}</span>
                      <span className="text-[10px] text-muted-foreground block">/ 100</span>
                    </div>
                    <div className="p-3 bg-muted/30 rounded-lg">
                      <span className="text-xs text-muted-foreground block">Stonewalling</span>
                      <span className="text-2xl font-bold text-slate-500">{state.result.gottman_breakdown.stonewalling_score}</span>
                      <span className="text-[10px] text-muted-foreground block">/ 100</span>
                    </div>
                  </div>
                  {state.result.gottman_breakdown.notes && (
                    <div className="mt-4 p-3 bg-muted/30 rounded-lg border text-xs text-muted-foreground leading-relaxed">
                      <span className="font-semibold text-foreground">Clinical SPAFF & Attachment Telemetry:</span>{" "}
                      {state.result.gottman_breakdown.notes}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Emotional Timeline */}
            {state.result.timeline_events && state.result.timeline_events.length > 0 && (
              <Card className="p-6">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold">Key Emotional Events</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="space-y-3">
                    {state.result.timeline_events.map((ev, i) => (
                      <div key={i} className="p-3 rounded-md bg-muted/30 border flex items-center justify-between text-sm">
                        <div>
                          <span className="font-semibold">{ev.speaker}</span>
                          <span className="text-xs text-muted-foreground ml-2">[{ev.timestamp}]</span>
                          <p className="text-xs text-muted-foreground mt-0.5">{ev.label}</p>
                          {ev.message && <p className="text-xs italic mt-1 text-foreground/80">"{ev.message}"</p>}
                        </div>
                        <span className={cn(
                          "px-2 py-0.5 rounded text-xs font-semibold",
                          ev.sentiment_impact > 0 ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                        )}>
                          {ev.sentiment_impact > 0 ? `+${ev.sentiment_impact}` : ev.sentiment_impact}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Relationship Repair or Vitality Blueprint */}
            {state.result.repair_blueprint ? (() => {
              const isHealthy = state.result.repair_blueprint.blueprint_type === "healthy_bond" || state.result.verdict === "Healthy";
              return (
                <Card className={cn(
                  "p-6 shadow-md border",
                  isHealthy ? "border-emerald-500/30 bg-gradient-to-b from-card to-emerald-50/10" : "border-primary/30"
                )}>
                  <CardHeader className="p-0 pb-6 border-b">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl font-bold flex items-center gap-2 text-foreground">
                          <Sparkles className={cn("w-5 h-5", isHealthy ? "text-emerald-500" : "text-primary")} /> 
                          {state.result.repair_blueprint.headline || (isHealthy ? "Relationship Vitality & Connection Blueprint" : "Relationship Repair Blueprint")}
                        </CardTitle>
                        <p className="text-xs text-muted-foreground mt-1">
                          {isHealthy 
                            ? "Celebration of mutual fondness, secure communication rhythms, and daily connection rituals"
                            : "Brutally honest diagnostic truths paired with compassionate, scientifically validated repair pathways"}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0 pt-6 space-y-6">
                    {/* Section 1: Strength of Bond (Healthy) or Brutal Truth (Conflict) */}
                    <div className={cn(
                      "p-4 rounded-lg border",
                      isHealthy 
                        ? "bg-emerald-50/80 border-emerald-200 text-emerald-950 dark:bg-emerald-950/20 dark:border-emerald-900/50 dark:text-emerald-200" 
                        : "bg-rose-50/80 border-rose-200 text-rose-950 dark:bg-rose-950/20 dark:border-rose-900/50 dark:text-rose-200"
                    )}>
                      <span className={cn(
                        "text-xs font-bold uppercase tracking-wider block mb-1",
                        isHealthy ? "text-emerald-700 dark:text-emerald-400" : "text-rose-700 dark:text-rose-400"
                      )}>
                        {isHealthy ? "🛡️ The Strength of Your Bond (What is working well)" : "⚠️ The Brutal Truth (What is really happening)"}
                      </span>
                      <p className="text-sm leading-relaxed">
                        {state.result.repair_blueprint.brutal_truth_summary}
                      </p>
                    </div>

                    {/* Section 2: Path Forward */}
                    <div className="p-4 rounded-lg bg-blue-50/80 border border-blue-200 text-blue-950 dark:bg-blue-950/20 dark:border-blue-900/50 dark:text-blue-200">
                      <span className="text-xs font-bold uppercase tracking-wider text-blue-700 dark:text-blue-400 block mb-1">
                        {isHealthy ? "🌱 The Path Forward (Cultivating Long-Term Intimacy)" : "🌱 The Hopeful Path Forward (Why this bond is worth fighting for)"}
                      </span>
                      <p className="text-sm leading-relaxed">
                        {state.result.repair_blueprint.hopeful_path_summary}
                      </p>
                    </div>

                    {/* Section 3: Person Diagnostics */}
                    {state.result.repair_blueprint.person_diagnostics && state.result.repair_blueprint.person_diagnostics.length > 0 && (
                      <div className="space-y-4 pt-2">
                        <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                          {isHealthy ? "Individual Dynamics & Communication Strengths" : "Individual Diagnostics: Specific Behavioral Pitfalls"}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {state.result.repair_blueprint.person_diagnostics.map((person, idx) => (
                            <div key={idx} className="p-4 rounded-lg border bg-card/60 space-y-3 flex flex-col justify-between">
                              <div className="space-y-3">
                                <div className="flex items-center justify-between border-b pb-2">
                                  <div>
                                    <span className="font-bold text-base text-foreground">{person.name}</span>
                                    <p className="text-xs text-muted-foreground">{person.attachment_style}</p>
                                  </div>
                                  <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary">
                                    Partner {idx === 0 ? "1" : "2"}
                                  </span>
                                </div>

                                <div>
                                  <span className={cn(
                                    "text-xs font-bold uppercase tracking-wider block mb-1.5",
                                    isHealthy ? "text-emerald-600 dark:text-emerald-400" : "text-destructive"
                                  )}>
                                    {isHealthy ? "✨ Observed Communication Strengths:" : "⚠️ Specific Behavioral Pitfalls:"}
                                  </span>
                                  <ul className="space-y-1.5 text-xs text-foreground/90">
                                    {person.primary_issues.map((issue, iIdx) => (
                                      <li key={iIdx} className="flex items-start gap-1.5">
                                        <span className={cn("font-bold", isHealthy ? "text-emerald-500" : "text-destructive")}>•</span>
                                        <span>{issue}</span>
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {person.strengths && person.strengths.length > 0 && (
                                  <div>
                                    <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400 block mb-1.5">
                                      🌱 Positive Relational Habits:
                                    </span>
                                    <ul className="space-y-1.5 text-xs text-foreground/90">
                                      {person.strengths.map((str, sIdx) => (
                                        <li key={sIdx} className="flex items-start gap-1.5">
                                          <span className="text-emerald-600 dark:text-emerald-400 font-bold">•</span>
                                          <span>{str}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}
                              </div>

                              <div className="p-3 rounded bg-muted/40 border-l-2 border-primary text-xs space-y-1 mt-2">
                                <span className="font-bold text-foreground block">
                                  {isHealthy ? "🎯 Recommended Daily Habit:" : "🎯 Individual Homework:"}
                                </span>
                                <p className="text-muted-foreground leading-relaxed">{person.action_plan}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Section 4: Protocols */}
                    <div className="space-y-4 pt-2">
                      <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                        {isHealthy ? "Proactive Connection Rituals & Daily Micro-Habits" : "Targeted Behavioral Repair Protocols & Exact Scripts"}
                      </h4>
                      <div className="grid grid-cols-1 gap-4">
                        {state.result.repair_blueprint.protocols.map((proto, idx) => (
                          <div key={idx} className="p-4 rounded-lg border bg-card hover:border-primary/40 transition-colors space-y-2">
                            <div className="flex items-start justify-between gap-2">
                              <span className="font-semibold text-sm text-foreground">{idx + 1}. {proto.title}</span>
                              <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-primary/10 text-primary whitespace-nowrap">
                                {proto.principle}
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground">{proto.action}</p>
                            <div className="p-2.5 rounded bg-muted/40 border-l-2 border-primary font-mono text-xs text-foreground/90 italic">
                              "{proto.script}"
                            </div>
                            <p className="text-[11px] font-medium text-amber-700 dark:text-amber-400">
                              {isHealthy ? "★ Golden Rule:" : "★ Non-Negotiable Rule:"} {proto.rule}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })() : state.result.actionable_advice && state.result.actionable_advice.length > 0 && (
              <Card className="p-6">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold">Actionable Recommendations</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <ul className="space-y-3 text-sm">
                    {state.result.actionable_advice.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-primary font-bold">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Normalized Conversation Transcript */}
            {state.result.normalized_conversation && state.result.normalized_conversation.length > 0 && (
              <Card className="p-6">
                <CardHeader className="p-0 pb-4">
                  <CardTitle className="text-base font-semibold flex items-center gap-2">
                    <FileText className="w-5 h-5 text-muted-foreground" /> Normalized English Conversation
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="max-h-72 overflow-y-auto space-y-2 p-3 bg-muted/20 rounded-md text-xs font-mono">
                    {state.result.normalized_conversation.map((m, idx) => (
                      <div key={idx} className="border-b pb-1 last:border-0">
                        <span className="font-bold text-foreground">{m.original_sender}:</span>{" "}
                        <span className="text-muted-foreground">{m.normalized_text}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Disclaimer Footer */}
        <footer className="pt-8 border-t text-center text-xs text-muted-foreground space-y-1">
          <p>
            IntimacyLens is an AI-powered diagnostic tool for self-reflection and communication insights.
          </p>
          <p>
            It is not licensed psychological or psychiatric counsel. All processing takes place locally on your machine.
          </p>
        </footer>

      </div>
    </div>
  );
}