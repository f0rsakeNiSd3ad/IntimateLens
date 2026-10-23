"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  ArrowLeft,
  AlertCircle, 
  Info, 
  Heart, 
  ShieldAlert, 
  Activity,
  CheckCircle2,
  XCircle,
  FileText
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressRing } from "@/components/ui/progress-ring";
import { cn } from "@/lib/utils";

import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from "recharts";

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

export default function DashboardPage() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem("latest_analysis");
      if (stored) {
        setResult(JSON.parse(stored));
      }
    } catch (e) {
      console.error("Failed to load analysis from sessionStorage", e);
    } finally {
      setLoading(false);
    }
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="text-center space-y-3">
          <Activity className="h-8 w-8 animate-pulse text-primary mx-auto" />
          <p className="text-sm text-muted-foreground">Loading relationship telemetry...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8 bg-background">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <Info className="h-12 w-12 text-muted-foreground mx-auto" />
          <h2 className="text-xl font-bold">No Analysis Data Available</h2>
          <p className="text-sm text-muted-foreground">
            Please upload a conversation transcript to generate psychological and relationship metrics.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-md bg-primary text-primary-foreground font-medium text-sm hover:bg-primary/90 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Go to File Upload
          </Link>
        </Card>
      </div>
    );
  }

  const speakerA = result.speaker_a || result.normalized_conversation?.[0]?.original_sender || "Person A";
  const speakerB = result.speaker_b || 
    result.normalized_conversation?.find(m => m.original_sender && m.original_sender !== speakerA)?.original_sender || 
    "Person B";

  const affectionData = [
    { 
      name: speakerA, 
      affection: result.affection_levels[speakerA] ?? result.affection_levels.person_a ?? 50, 
      fill: "hsl(var(--primary))" 
    },
    { 
      name: speakerB, 
      affection: result.affection_levels[speakerB] ?? result.affection_levels.person_b ?? 50, 
      fill: "hsl(var(--accent))" 
    },
  ];

  const gottmanData = result.gottman_breakdown ? [
    { name: "Criticism", score: result.gottman_breakdown.criticism_score, color: "#f59e0b" },
    { name: "Contempt", score: result.gottman_breakdown.contempt_score, color: "#ef4444" },
    { name: "Defensiveness", score: result.gottman_breakdown.defensiveness_score, color: "#3b82f6" },
    { name: "Stonewalling", score: result.gottman_breakdown.stonewalling_score, color: "#64748b" },
  ] : [];

  return (
    <div className="min-h-screen bg-background p-6 md:p-12 font-sans antialiased text-foreground">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Navigation / Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <Link 
              href="/upload" 
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground mb-2"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Upload
            </Link>
            <h1 className="text-3xl font-extrabold tracking-tight">Psychological Analysis Dashboard</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              Comprehensive Gottman framework & affection telemetry
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className={cn(
              "px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border",
              result.verdict === "Healthy" || result.verdict === "Repairable" ? "bg-emerald-100 text-emerald-800 border-emerald-300" :
              result.verdict === "Critical" ? "bg-amber-100 text-amber-800 border-amber-300" :
              "bg-rose-100 text-rose-800 border-rose-300"
            )}>
              Verdict: {result.verdict}
            </span>
          </div>
        </div>

        {/* Top Telemetry Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Toxicity Gauge */}
          <Card className="p-6 flex flex-col items-center justify-center text-center">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Overall Toxicity Index
              </CardTitle>
            </CardHeader>
            <ProgressRing 
              value={result.toxicity_score} 
              size={130} 
              strokeWidth={12}
              colorClassName={
                result.toxicity_score >= 60 ? "text-destructive" :
                result.toxicity_score >= 35 ? "text-amber-500" : "text-emerald-500"
              }
            />
            <div className="mt-3">
              <span className="text-3xl font-black">{result.toxicity_score}</span>
              <span className="text-sm text-muted-foreground"> / 100</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {result.toxicity_score >= 60 ? "High toxicity risk identified" :
               result.toxicity_score >= 35 ? "Moderate emotional friction" : "Healthy emotional environment"}
            </p>
          </Card>

          {/* Affection Comparison Bar Chart */}
          <Card className="p-6 md:col-span-2">
            <CardHeader className="p-0 pb-3 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Affection & Validation Levels: {speakerA} vs {speakerB}
              </CardTitle>
              <Heart className="w-4 h-4 text-primary" />
            </CardHeader>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={affectionData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(val: number) => [`${val}%`, "Affection Score"]}
                    contentStyle={{ borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="affection" radius={[6, 6, 0, 0]}>
                    {affectionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        {/* Gottman Four Horsemen Breakdown */}
        {result.gottman_breakdown && (
          <Card className="p-6">
            <CardHeader className="p-0 pb-4 flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base font-semibold">Gottman Four Horsemen Analysis</CardTitle>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Assessment of toxic conflict indicators (0 = absent, 100 = critical severity)
                </p>
              </div>
              <ShieldAlert className="w-5 h-5 text-primary" />
            </CardHeader>
            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={gottmanData} margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(val: number) => [`${val} / 100`, "Severity Score"]}
                    contentStyle={{ borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Bar dataKey="score" radius={[6, 6, 0, 0]}>
                    {gottmanData.map((entry, index) => (
                      <Cell key={`gottman-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            {result.gottman_breakdown.notes && (
              <div className="mt-4 p-3.5 bg-muted/40 rounded-lg border text-xs text-muted-foreground leading-relaxed">
                <span className="font-semibold text-foreground">Clinical SPAFF & Attachment Telemetry:</span>{" "}
                {result.gottman_breakdown.notes}
              </div>
            )}
          </Card>
        )}

        {/* Qualitative Observations: Red & Green Flags */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="p-6 border-red-200/50">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2 text-destructive">
                <XCircle className="w-4 h-4" /> Observed Communication Pitfalls
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ul className="space-y-2 text-sm">
                {result.key_red_flags.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-destructive font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          <Card className="p-6 border-emerald-200/50">
            <CardHeader className="p-0 pb-3">
              <CardTitle className="text-sm font-semibold flex items-center gap-2 text-emerald-600">
                <CheckCircle2 className="w-4 h-4" /> Healthy Relational Patterns
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ul className="space-y-2 text-sm">
                {result.key_green_flags.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-600 font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Emotional Timeline */}
        {result.timeline_events && result.timeline_events.length > 0 && (
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-base font-semibold">Interaction Timeline & Valence Spikes</CardTitle>
            </CardHeader>
            <CardContent className="p-0 space-y-3">
              {result.timeline_events.map((ev, i) => (
                <div key={i} className="p-3.5 rounded-lg border bg-card flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-sm">{ev.speaker}</span>
                      <span className="text-xs text-muted-foreground">[{ev.timestamp}]</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5">{ev.label}</p>
                    {ev.message && <p className="text-xs italic mt-1.5 text-foreground/80">"{ev.message}"</p>}
                  </div>
                  <span className={cn(
                    "px-2.5 py-1 rounded text-xs font-bold whitespace-nowrap",
                    ev.sentiment_impact > 0 ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                  )}>
                    {ev.sentiment_impact > 0 ? `+${ev.sentiment_impact}` : ev.sentiment_impact}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Relationship Repair or Vitality Blueprint */}
        {result.repair_blueprint ? (() => {
          const isHealthy = result.repair_blueprint.blueprint_type === "healthy_bond" || result.verdict === "Healthy";
          return (
            <Card className={cn(
              "p-6 shadow-md border",
              isHealthy ? "border-emerald-500/30 bg-gradient-to-b from-card to-emerald-50/10" : "border-primary/30"
            )}>
              <CardHeader className="p-0 pb-6 border-b">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-bold flex items-center gap-2 text-foreground">
                      <Heart className={cn("w-5 h-5", isHealthy ? "text-emerald-500" : "text-primary")} /> 
                      {result.repair_blueprint.headline || (isHealthy ? "Relationship Vitality & Connection Blueprint" : "Relationship Repair Blueprint")}
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
                    {result.repair_blueprint.brutal_truth_summary}
                  </p>
                </div>

                {/* Section 2: Path Forward */}
                <div className="p-4 rounded-lg bg-blue-50/80 border border-blue-200 text-blue-950 dark:bg-blue-950/20 dark:border-blue-900/50 dark:text-blue-200">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-700 dark:text-blue-400 block mb-1">
                    {isHealthy ? "🌱 The Path Forward (Cultivating Long-Term Intimacy)" : "🌱 The Hopeful Path Forward (Why this bond is worth fighting for)"}
                  </span>
                  <p className="text-sm leading-relaxed">
                    {result.repair_blueprint.hopeful_path_summary}
                  </p>
                </div>

                {/* Section 3: Person Diagnostics */}
                {result.repair_blueprint.person_diagnostics && result.repair_blueprint.person_diagnostics.length > 0 && (
                  <div className="space-y-4 pt-2">
                    <h4 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
                      {isHealthy ? "Individual Dynamics & Communication Strengths" : "Individual Diagnostics: Specific Behavioral Pitfalls"}
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {result.repair_blueprint.person_diagnostics.map((person, idx) => (
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
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.repair_blueprint.protocols.map((proto, idx) => (
                      <div key={idx} className="p-4 rounded-lg border bg-card hover:border-primary/40 transition-colors space-y-2 flex flex-col justify-between">
                        <div className="space-y-2">
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
                        </div>
                        <p className="text-[11px] font-medium text-amber-700 dark:text-amber-400 pt-2 border-t border-border/50">
                          {isHealthy ? "★ Golden Rule:" : "★ Non-Negotiable Rule:"} {proto.rule}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })() : result.actionable_advice && result.actionable_advice.length > 0 && (
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-base font-semibold">Recommended Therapeutic Actions</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <ol className="space-y-2.5 text-sm list-decimal list-inside">
                {result.actionable_advice.map((advice, i) => (
                  <li key={i} className="leading-relaxed">
                    <span className="font-medium text-foreground">{advice}</span>
                  </li>
                ))}
              </ol>
            </CardContent>
          </Card>
        )}

        {/* Normalized Conversation Section */}
        {result.normalized_conversation && result.normalized_conversation.length > 0 && (
          <Card className="p-6">
            <CardHeader className="p-0 pb-4">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <FileText className="w-5 h-5 text-muted-foreground" />
                Normalized Transcript
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-80 overflow-y-auto space-y-2 p-4 bg-muted/20 rounded-lg text-xs font-mono">
                {result.normalized_conversation.map((m, idx) => (
                  <div key={idx} className="border-b border-border/50 pb-1.5 last:border-0">
                    <span className="font-bold text-foreground">{m.original_sender}:</span>{" "}
                    <span className="text-muted-foreground">{m.normalized_text}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

      </div>
    </div>
  );
}