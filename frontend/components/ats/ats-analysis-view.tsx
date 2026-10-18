"use client";

import { useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowsClockwise,
  Check,
  CheckCircle,
  Clock,
  DownloadSimple,
  Eye,
  FileDoc,
  FilePdf,
  Info,
  Lightbulb,
  MagnifyingGlass,
  PencilSimple,
  ShieldCheck,
  Sparkle,
  Target,
  Warning,
  WarningCircle,
  XCircle,
} from "@phosphor-icons/react";
import {
  Badge,
  Button,
  Card,
  Modal,
  ProgressBar,
  SelectField,
} from "@/components/ui";
import { useApplyAtsSuggestions, useAtsAnalysis, useRunAtsAnalysis } from "@/hooks/use-ats";
import { useCvList, useExportDocx, useExportPdf } from "@/hooks/use-cv";
import { useJobList } from "@/hooks/use-jobs";
import { AppView } from "@/types";
import {
  ApplyATSSuggestionsResponse,
  ATSAnalysisResponse,
  ATSCheckCategory,
  ATSCheckItem,
  ATSCheckSeverity,
  GroundedKeywordSuggestion,
} from "@/types/ats";

interface AtsAnalysisViewProps {
  initialCvVersionId?: string;
  initialJobId?: string;
  onNavigate: (view: AppView) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onSelectCvVersion?: (versionId: string) => void;
}

export function AtsAnalysisView({
  initialCvVersionId,
  initialJobId,
  onNavigate,
  onToast,
  onSelectCvVersion,
}: AtsAnalysisViewProps) {
  // 1. Fetch available CV versions and job targets
  const { data: cvListData, isLoading: isCvLoading } = useCvList();
  const cvVersions = cvListData?.items || [];

  const { data: jobListData, isLoading: isJobsLoading } = useJobList();
  const jobs = jobListData?.items || [];

  // 2. Local selection state
  const [selectedCvId, setSelectedCvId] = useState<string>(
    initialCvVersionId || (cvVersions.length > 0 ? cvVersions[0].id : "")
  );
  const [selectedJobId, setSelectedJobId] = useState<string>(
    initialJobId || ""
  );

  const activeCvId = selectedCvId || (cvVersions.length > 0 ? cvVersions[0].id : undefined);
  const activeJobId = selectedJobId || undefined;

  // 3. TanStack Query hooks for ATS analysis & optimization
  const {
    data: analysisData,
    isLoading: isAnalysisLoading,
    isFetching,
    refetch,
  } = useAtsAnalysis(activeCvId, activeJobId, {
    enabled: Boolean(activeCvId),
  });

  const runAnalysisMutation = useRunAtsAnalysis();
  const applySuggestionsMutation = useApplyAtsSuggestions();
  const exportPdfMutation = useExportPdf();
  const exportDocxMutation = useExportDocx();

  // 4. Interactive optimization state
  const [acceptedSuggestionIds, setAcceptedSuggestionIds] = useState<Set<string>>(new Set());
  const [checkCategoryFilter, setCheckCategoryFilter] = useState<string>("all");
  const [checkStatusFilter, setCheckStatusFilter] = useState<string>("all");
  const [appliedResult, setAppliedResult] = useState<ApplyATSSuggestionsResponse | null>(null);
  const [appliedModalOpen, setAppliedModalOpen] = useState(false);

  // Active CV and Job objects
  const activeCv = useMemo(
    () => cvVersions.find((v) => v.id === activeCvId) || null,
    [cvVersions, activeCvId]
  );
  const activeJob = useMemo(
    () => jobs.find((j) => j.id === activeJobId) || null,
    [jobs, activeJobId]
  );

  const handleRunAnalysis = async () => {
    if (!activeCvId) {
      onToast("Select CV", "Please select a CV version to analyze.", "error");
      return;
    }
    try {
      await runAnalysisMutation.mutateAsync({
        cv_version_id: activeCvId,
        job_id: activeJobId,
      });
      onToast("Analysis Complete", "Explainable ATS compatibility audit updated.", "success");
    } catch {
      onToast("Analysis Failed", "Could not complete ATS analysis. Please try again.", "error");
    }
  };

  const handleToggleSuggestion = (suggestionId: string) => {
    setAcceptedSuggestionIds((prev) => {
      const next = new Set(prev);
      if (next.has(suggestionId)) {
        next.delete(suggestionId);
      } else {
        next.add(suggestionId);
      }
      return next;
    });
  };

  const handleApplySelectedSuggestions = async () => {
    if (!activeCvId || acceptedSuggestionIds.size === 0) {
      onToast("No Suggestions Selected", "Select at least one grounded keyword to apply.", "info");
      return;
    }

    try {
      const response = await applySuggestionsMutation.mutateAsync({
        cv_version_id: activeCvId,
        accepted_suggestion_ids: Array.from(acceptedSuggestionIds),
        job_id: activeJobId,
        new_version_name: activeCv ? `${activeCv.name} - ATS Optimized` : undefined,
      });

      setAppliedResult(response);
      setAppliedModalOpen(true);
      setAcceptedSuggestionIds(new Set());
      onToast("CV Optimized", `Created independent CV version with ${response.applied_suggestions_count} additions.`, "success");
    } catch {
      onToast("Error", "Could not apply optimizations. Please try again.", "error");
    }
  };

  const handleExportPdf = async () => {
    if (!activeCvId) return;
    try {
      await exportPdfMutation.mutateAsync({ id: activeCvId });
      onToast("PDF Export", "Downloading ATS-ready PDF document.", "success");
    } catch {
      onToast("Export Failed", "Could not export PDF.", "error");
    }
  };

  const handleExportDocx = async () => {
    if (!activeCvId) return;
    try {
      await exportDocxMutation.mutateAsync({ id: activeCvId });
      onToast("Word Export", "Downloading editable Microsoft Word (.docx) file.", "success");
    } catch {
      onToast("Export Failed", "Could not export Word document.", "error");
    }
  };

  // Derive score presentation
  const overallScore = analysisData?.overall_score ?? 0;
  const scoreTone = overallScore >= 80 ? "green" : overallScore >= 60 ? "amber" : "red";
  const scoreLabel =
    overallScore >= 80
      ? "Strong ATS Baseline"
      : overallScore >= 60
      ? "Moderate Compatibility"
      : "Requires Optimization";

  // Filter parser checks
  const checks = analysisData?.checks || [];
  const filteredChecks = useMemo(() => {
    return checks.filter((c) => {
      if (checkStatusFilter !== "all" && c.status !== checkStatusFilter) return false;
      if (checkCategoryFilter !== "all" && c.category !== checkCategoryFilter) return false;
      return true;
    });
  }, [checks, checkStatusFilter, checkCategoryFilter]);

  const warningCount = checks.filter((c) => c.status === "warning").length;
  const reviewCount = checks.filter((c) => c.status === "review").length;
  const passCount = checks.filter((c) => c.status === "pass").length;

  // Group keyword suggestions into grounded vs unsupported
  const suggestions = analysisData?.suggestions || [];
  const groundedSuggestions = suggestions.filter((s) => s.is_grounded_in_profile);
  const unsupportedGaps = suggestions.filter((s) => !s.is_grounded_in_profile);

  const keywords = analysisData?.keywords || [];
  const overusedKeywords = keywords.filter((k) => k.is_overused);

  return (
    <div className="page-frame">
      {/* Header Bar */}
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Document Studio</span>
          <h1 className="page-title">ATS Analysis & Keyword Optimization</h1>
          <p className="page-subtitle">
            Explainable compatibility audit evaluating layout friction, keyword density, and grounded qualification match.
          </p>
        </div>
        <div className="page-header-actions" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <Button
            variant="ghost"
            icon={<ArrowLeft size={16} aria-hidden="true" />}
            onClick={() => onNavigate("cv-generation")}
          >
            CV Versions
          </Button>
          <Button
            variant="secondary"
            icon={<FilePdf size={16} aria-hidden="true" />}
            loading={exportPdfMutation.isPending}
            onClick={handleExportPdf}
            disabled={!activeCvId}
          >
            Export PDF
          </Button>
          <Button
            variant="secondary"
            icon={<FileDoc size={16} aria-hidden="true" />}
            loading={exportDocxMutation.isPending}
            onClick={handleExportDocx}
            disabled={!activeCvId}
          >
            Export Word
          </Button>
          <Button
            variant="primary"
            icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
            loading={runAnalysisMutation.isPending || isFetching}
            onClick={handleRunAnalysis}
            disabled={!activeCvId}
          >
            {runAnalysisMutation.isPending || isFetching ? "Analyzing…" : "Run ATS Audit"}
          </Button>
        </div>
      </div>

      {/* Selector Controls Bar */}
      <Card style={{ padding: "1.25rem", marginBottom: "1.5rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1rem", alignItems: "end" }}>
          <SelectField
            label="Select CV Version"
            id="ats-cv-select"
            value={activeCvId || ""}
            onChange={(e) => setSelectedCvId(e.target.value)}
          >
            {cvVersions.length === 0 ? (
              <option value="">No CV versions available</option>
            ) : (
              cvVersions.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} ({v.status})
                </option>
              ))
            )}
          </SelectField>

          <SelectField
            label="Target Job (Optional)"
            id="ats-job-select"
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
          >
            <option value="">General ATS Baseline (No target job)</option>
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title} at {j.company_name}
              </option>
            ))}
          </SelectField>

          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              variant="secondary"
              icon={<ArrowsClockwise size={16} aria-hidden="true" />}
              loading={isFetching}
              onClick={() => refetch()}
              disabled={!activeCvId}
              title="Refresh current analysis"
            >
              Refresh
            </Button>
            {activeCvId ? (
              <Button
                variant="quiet"
                icon={<PencilSimple size={16} aria-hidden="true" />}
                onClick={() => {
                  if (onSelectCvVersion) onSelectCvVersion(activeCvId);
                  onNavigate("cv-editor");
                }}
              >
                Edit in Studio
              </Button>
            ) : null}
          </div>
        </div>
      </Card>

      {/* Empty State if no CV version */}
      {!activeCvId && !isCvLoading ? (
        <Card style={{ padding: "3rem 1.5rem", textAlign: "center" }}>
          <MagnifyingGlass size={48} style={{ color: "var(--fg-muted, #71717a)", margin: "0 auto 1rem" }} />
          <h2 style={{ fontSize: "1.25rem", margin: "0 0 0.5rem" }}>No CV Version Selected</h2>
          <p style={{ color: "var(--fg-muted, #a1a1aa)", maxWidth: "450px", margin: "0 auto 1.5rem" }}>
            Select an existing CV version or create one from your candidate knowledge base to run an explainable ATS audit.
          </p>
          <Button variant="primary" onClick={() => onNavigate("cv-generation")}>
            Go to CV Versions
          </Button>
        </Card>
      ) : isAnalysisLoading && !analysisData ? (
        /* Loading skeleton */
        <Card style={{ padding: "3rem 1.5rem", textAlign: "center" }}>
          <Sparkle size={36} className="spin" style={{ color: "var(--color-primary-400, #38bdf8)", margin: "0 auto 1rem" }} />
          <p style={{ fontSize: "1.1rem", margin: 0 }}>Evaluating layout, keywords, and parsing flow…</p>
        </Card>
      ) : analysisData ? (
        <>
          {/* Top Score & High-Level Breakdown Grid */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "1.25rem", marginBottom: "1.5rem" }}>
            {/* Overall Score Card */}
            <Card style={{ padding: "1.5rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <span className="page-eyebrow">Overall Score</span>
                  <h2 style={{ fontSize: "2.75rem", margin: "0.25rem 0 0", fontWeight: 700, color: `var(--color-${scoreTone}-400, #38bdf8)` }}>
                    {overallScore}
                    <span style={{ fontSize: "1.25rem", color: "var(--fg-muted, #71717a)", fontWeight: 400 }}>/100</span>
                  </h2>
                </div>
                <Badge tone={scoreTone}>{scoreLabel}</Badge>
              </div>

              <div style={{ marginTop: "1rem" }}>
                <ProgressBar value={overallScore} tone={scoreTone} />
                <p style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", margin: "0.5rem 0 0" }}>
                  Mode: {analysisData.scoring_mode === "job_targeted" ? "Targeted Job Requirements" : "General Baseline (No Job Target)"}
                </p>
              </div>
            </Card>

            {/* Keyword Coverage Card */}
            <Card style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                <div>
                  <span className="page-eyebrow">Keyword Alignment</span>
                  <h3 style={{ fontSize: "1.75rem", margin: "0.25rem 0 0", fontWeight: 700 }}>
                    {analysisData.keyword_coverage_percentage}%
                  </h3>
                </div>
                <Badge tone={analysisData.keyword_coverage_percentage >= 70 ? "green" : "amber"}>
                  {keywords.filter((k) => k.is_present).length} of {keywords.length} terms
                </Badge>
              </div>
              <ProgressBar value={analysisData.keyword_coverage_percentage} tone={analysisData.keyword_coverage_percentage >= 70 ? "green" : "amber"} />
              <p style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", margin: "0.75rem 0 0" }}>
                Total word count: <strong>{analysisData.total_words} words</strong>.
                {overusedKeywords.length > 0 ? (
                  <span style={{ color: "var(--color-amber-400, #fbbf24)", marginLeft: 6 }}>
                    ({overusedKeywords.length} term(s) with high repetition)
                  </span>
                ) : (
                  <span style={{ color: "var(--color-emerald-400, #34d399)", marginLeft: 6 }}>
                    (Natural density distribution)
                  </span>
                )}
              </p>
            </Card>

            {/* Parser Safety Card */}
            <Card style={{ padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                <div>
                  <span className="page-eyebrow">Parser Checks Audit</span>
                  <h3 style={{ fontSize: "1.75rem", margin: "0.25rem 0 0", fontWeight: 700 }}>
                    {passCount}/{checks.length} Pass
                  </h3>
                </div>
                <Badge tone={warningCount > 0 ? "amber" : "green"}>
                  {warningCount} Warnings · {reviewCount} Reviews
                </Badge>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
                <span style={{ fontSize: "0.8125rem", color: "var(--color-emerald-400, #34d399)", display: "flex", alignItems: "center", gap: 4 }}>
                  <CheckCircle size={15} weight="fill" /> {passCount} passed
                </span>
                <span style={{ fontSize: "0.8125rem", color: "var(--color-amber-400, #fbbf24)", display: "flex", alignItems: "center", gap: 4 }}>
                  <WarningCircle size={15} weight="fill" /> {warningCount} warnings
                </span>
                <span style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", display: "flex", alignItems: "center", gap: 4 }}>
                  <Info size={15} /> {reviewCount} reviews
                </span>
              </div>
            </Card>
          </div>

          {/* Explainable Component Breakdown */}
          <Card style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", margin: "0 0 1rem", fontWeight: 600 }}>
              Explainable Scoring Breakdown
            </h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem" }}>
              {analysisData.components.map((comp) => {
                const pct = Math.round((comp.score / comp.max_score) * 100);
                return (
                  <div
                    key={comp.name}
                    style={{
                      padding: "1rem",
                      borderRadius: "var(--radius-md, 8px)",
                      backgroundColor: "var(--bg-subtle, rgba(255,255,255,0.03))",
                      border: "1px solid var(--border-subtle, rgba(255,255,255,0.08))",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                      <strong style={{ fontSize: "0.9rem" }}>{comp.name}</strong>
                      <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--color-primary-400, #38bdf8)" }}>
                        {comp.score}/{comp.max_score} pts
                      </span>
                    </div>
                    <ProgressBar value={pct} tone={pct >= 80 ? "green" : pct >= 60 ? "amber" : "red"} />
                    <p style={{ fontSize: "0.8rem", color: "var(--fg-muted, #a1a1aa)", margin: "0.5rem 0 0", lineHeight: 1.4 }}>
                      {comp.explanation}
                    </p>
                    {comp.deductions.length > 0 && (
                      <div style={{ marginTop: "0.5rem", borderTop: "1px dashed var(--border-subtle, rgba(255,255,255,0.1))", paddingTop: "0.4rem" }}>
                        {comp.deductions.map((ded, i) => (
                          <span key={i} style={{ display: "block", fontSize: "0.75rem", color: "var(--color-amber-400, #fbbf24)" }}>
                            • {ded}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Grounded Keyword Optimization Section */}
          <Card style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1rem" }}>
              <div>
                <span className="page-eyebrow">Keyword Optimization</span>
                <h3 style={{ fontSize: "1.1rem", margin: "0.25rem 0 0", fontWeight: 600 }}>
                  Grounded Career Suggestions & Missing Terminology
                </h3>
                <p style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", margin: "0.25rem 0 0" }}>
                  Items substantiated by your Candidate Knowledge Base can be accepted and inserted. Unsupported qualifications are strictly flagged to prevent fabrication.
                </p>
              </div>

              {groundedSuggestions.length > 0 && (
                <Button
                  variant="primary"
                  size="sm"
                  icon={<Sparkle size={15} weight="fill" />}
                  loading={applySuggestionsMutation.isPending}
                  disabled={acceptedSuggestionIds.size === 0 || applySuggestionsMutation.isPending}
                  onClick={handleApplySelectedSuggestions}
                >
                  Apply {acceptedSuggestionIds.size} Selected Optimization(s)
                </Button>
              )}
            </div>

            {/* Grounded Suggestions List */}
            {groundedSuggestions.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.5rem" }}>
                {groundedSuggestions.map((sug) => {
                  const isAccepted = acceptedSuggestionIds.has(sug.id);
                  return (
                    <div
                      key={sug.id}
                      onClick={() => handleToggleSuggestion(sug.id)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        padding: "0.85rem 1rem",
                        borderRadius: "var(--radius-md, 8px)",
                        backgroundColor: isAccepted ? "rgba(56, 189, 248, 0.08)" : "var(--bg-subtle, rgba(255,255,255,0.02))",
                        border: isAccepted ? "1px solid var(--color-primary-500, #0284c7)" : "1px solid var(--border-subtle, rgba(255,255,255,0.08))",
                        cursor: "pointer",
                        transition: "all 0.15s ease",
                      }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
                        <div
                          style={{
                            width: "20px",
                            height: "20px",
                            borderRadius: "4px",
                            border: isAccepted ? "1px solid var(--color-primary-400, #38bdf8)" : "1px solid var(--border-subtle, #71717a)",
                            backgroundColor: isAccepted ? "var(--color-primary-500, #0284c7)" : "transparent",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                          }}
                        >
                          {isAccepted && <Check size={14} color="#fff" weight="bold" />}
                        </div>

                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                            <strong style={{ fontSize: "0.95rem" }}>{sug.keyword}</strong>
                            {sug.is_mandatory && <Badge tone="red">Required</Badge>}
                            <Badge tone="green">Grounded in Knowledge Base</Badge>
                          </div>
                          <span style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)" }}>
                            {sug.suggested_action} · <span style={{ color: "var(--color-emerald-400, #34d399)" }}>{sug.grounding_evidence}</span>
                          </span>
                        </div>
                      </div>

                      <Button
                        variant={isAccepted ? "secondary" : "quiet"}
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleSuggestion(sug.id);
                        }}
                      >
                        {isAccepted ? "Selected" : "Accept Suggestion"}
                      </Button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)", fontStyle: "italic", margin: "0.5rem 0 1.5rem" }}>
                No candidate-grounded missing keywords detected. Your current skills thoroughly cover substantiated requirements.
              </p>
            )}

            {/* Unsupported Gaps Warning Box */}
            {unsupportedGaps.length > 0 && (
              <div
                style={{
                  padding: "1rem",
                  borderRadius: "var(--radius-md, 8px)",
                  backgroundColor: "rgba(239, 68, 68, 0.05)",
                  border: "1px solid rgba(239, 68, 68, 0.2)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <ShieldCheck size={18} color="var(--color-danger, #ef4444)" />
                  <strong style={{ fontSize: "0.875rem", color: "var(--color-danger, #ef4444)" }}>
                    Unverified Qualification Gaps (Zero-Hallucination Guard)
                  </strong>
                </div>
                <p style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", margin: "0 0 0.75rem" }}>
                  The target job highlights the following qualifications, but they are <strong>absent from your career profile</strong>. To protect career integrity, they will not be hallucinated into your CV.
                </p>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {unsupportedGaps.map((gap) => (
                    <span
                      key={gap.id}
                      style={{
                        padding: "0.25rem 0.6rem",
                        borderRadius: "4px",
                        fontSize: "0.8rem",
                        backgroundColor: "rgba(255,255,255,0.05)",
                        border: "1px solid rgba(255,255,255,0.1)",
                        color: "var(--fg-muted, #e4e4e7)",
                        display: "flex",
                        alignItems: "center",
                        gap: "0.35rem",
                      }}
                    >
                      {gap.keyword} {gap.is_mandatory && <span style={{ color: "var(--color-danger, #ef4444)", fontSize: "0.7rem" }}>(Required)</span>}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Card>

          {/* Parser Checks & Format Audit */}
          <Card style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem", marginBottom: "1rem" }}>
              <div>
                <span className="page-eyebrow">Parser Checks Audit</span>
                <h3 style={{ fontSize: "1.1rem", margin: "0.25rem 0 0", fontWeight: 600 }}>
                  Structural Headings, Date Logic & Layout Risk
                </h3>
              </div>

              {/* Filter controls */}
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <span style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)" }}>Filter:</span>
                {(["all", "warning", "review", "pass"] as const).map((filter) => (
                  <Button
                    key={filter}
                    variant={checkStatusFilter === filter ? "secondary" : "quiet"}
                    size="sm"
                    onClick={() => setCheckStatusFilter(filter)}
                  >
                    {filter === "all" ? "All" : filter.toUpperCase()}
                  </Button>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {filteredChecks.length === 0 ? (
                <p style={{ color: "var(--fg-muted, #a1a1aa)", fontSize: "0.875rem", margin: "1rem 0" }}>
                  No checks match the active filter.
                </p>
              ) : (
                filteredChecks.map((chk) => (
                  <div
                    key={chk.id}
                    style={{
                      padding: "0.85rem 1rem",
                      borderRadius: "var(--radius-md, 8px)",
                      backgroundColor: "var(--bg-subtle, rgba(255,255,255,0.02))",
                      border: "1px solid var(--border-subtle, rgba(255,255,255,0.08))",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.25rem" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                        {chk.status === "pass" ? (
                          <CheckCircle size={16} color="var(--color-emerald-400, #34d399)" weight="fill" />
                        ) : chk.status === "warning" ? (
                          <WarningCircle size={16} color="var(--color-amber-400, #fbbf24)" weight="fill" />
                        ) : (
                          <Info size={16} color="var(--color-primary-400, #38bdf8)" />
                        )}
                        <strong style={{ fontSize: "0.9rem" }}>{chk.label}</strong>
                      </div>
                      <Badge tone={chk.status === "pass" ? "green" : chk.status === "warning" ? "amber" : "neutral"}>
                        {chk.status.toUpperCase()}
                      </Badge>
                    </div>
                    <p style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", margin: "0.25rem 0 0", lineHeight: 1.4 }}>
                      {chk.detail}
                    </p>
                    {chk.recommendation && (
                      <p style={{ fontSize: "0.75rem", color: "var(--color-primary-300, #7dd3fc)", margin: "0.4rem 0 0" }}>
                        💡 Recommendation: {chk.recommendation}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          </Card>

          {/* Keyword Frequency & Density Table */}
          <Card style={{ padding: "1.5rem", marginBottom: "1.5rem" }}>
            <div style={{ marginBottom: "1rem" }}>
              <span className="page-eyebrow">Keyword Frequency & Density</span>
              <h3 style={{ fontSize: "1.1rem", margin: "0.25rem 0 0", fontWeight: 600 }}>
                Term Distribution & Repetition Safeguards
              </h3>
            </div>

            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border-subtle, rgba(255,255,255,0.1))", textAlign: "left" }}>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Term</th>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Target Role</th>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Count in CV</th>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Density (%)</th>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Sections Found</th>
                    <th style={{ padding: "0.5rem 0.75rem" }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {keywords.map((kw, i) => (
                    <tr
                      key={i}
                      style={{
                        borderBottom: "1px solid var(--border-subtle, rgba(255,255,255,0.05))",
                        backgroundColor: kw.is_overused ? "rgba(245, 158, 11, 0.08)" : "transparent",
                      }}
                    >
                      <td style={{ padding: "0.6rem 0.75rem", fontWeight: 600 }}>{kw.keyword}</td>
                      <td style={{ padding: "0.6rem 0.75rem" }}>
                        {kw.is_mandatory ? <Badge tone="red">Required</Badge> : <Badge tone="neutral">Preferred</Badge>}
                      </td>
                      <td style={{ padding: "0.6rem 0.75rem" }}>{kw.count}</td>
                      <td style={{ padding: "0.6rem 0.75rem" }}>{kw.density_percentage}%</td>
                      <td style={{ padding: "0.6rem 0.75rem", color: "var(--fg-muted, #a1a1aa)" }}>
                        {kw.locations_found.length > 0 ? kw.locations_found.join(", ") : "—"}
                      </td>
                      <td style={{ padding: "0.6rem 0.75rem" }}>
                        {kw.is_overused ? (
                          <Badge tone="amber">Stuffing Risk</Badge>
                        ) : kw.is_present ? (
                          <Badge tone="green">Present</Badge>
                        ) : (
                          <Badge tone="neutral">Missing</Badge>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Mandatory Heuristic Disclaimer */}
          <div
            style={{
              padding: "1rem 1.25rem",
              borderRadius: "var(--radius-md, 8px)",
              backgroundColor: "rgba(56, 189, 248, 0.04)",
              border: "1px solid rgba(56, 189, 248, 0.15)",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              marginBottom: "1.5rem",
            }}
          >
            <Info size={20} color="var(--color-primary-400, #38bdf8)" style={{ flexShrink: 0 }} />
            <p style={{ margin: 0, fontSize: "0.8125rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.5 }}>
              {analysisData.disclaimer}
            </p>
          </div>

          {/* Bottom Workflow Action Bar */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.75rem" }}>
            <Button
              variant="ghost"
              icon={<ArrowLeft size={16} aria-hidden="true" />}
              onClick={() => onNavigate("cv-generation")}
            >
              Back to CV Studio
            </Button>
            <Button
              variant="primary"
              icon={<ArrowRight size={16} aria-hidden="true" />}
              onClick={() => onNavigate("cover-email")}
            >
              Continue to Cover Email
            </Button>
          </div>
        </>
      ) : null}

      {/* Optimization Applied Modal */}
      <Modal
        open={appliedModalOpen}
        onClose={() => setAppliedModalOpen(false)}
        title="ATS Optimization Applied"
        description={`Created independent CV Version "${appliedResult?.new_version_name}" with ${appliedResult?.applied_suggestions_count} grounded additions.`}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", width: "100%" }}>
            <Button variant="ghost" onClick={() => setAppliedModalOpen(false)}>
              Close
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                setAppliedModalOpen(false);
                if (appliedResult && onSelectCvVersion) {
                  onSelectCvVersion(appliedResult.new_version_id);
                }
                onNavigate("cv-editor");
              }}
            >
              Open in CV Editor
            </Button>
          </div>
        }
      >
        <p style={{ fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.5, margin: "0 0 1rem" }}>
          Your original CV and Candidate Profile remain 100% untouched. The newly created version contains your accepted grounded skills and is ready for export or further styling.
        </p>
      </Modal>
    </div>
  );
}
