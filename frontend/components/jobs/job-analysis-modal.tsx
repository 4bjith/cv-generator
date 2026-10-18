"use client";

import { useMemo, useState } from "react";
import {
  ArrowUpRight,
  ArrowsClockwise,
  CheckCircle,
  FileText,
  MagnifyingGlass,
  Question,
  ShieldCheck,
  Sparkle,
  WarningCircle,
  XCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Modal } from "@/components/ui";
import { useAnalyzeJob, useJobAnalysis } from "@/hooks/use-jobs";
import { CandidateMatchStatus, JobRequirementItem, JobTarget } from "@/types/job";

interface JobAnalysisModalProps {
  job: JobTarget | null;
  open: boolean;
  onClose: () => void;
  onCreateCvRequest: (job: JobTarget) => void;
  onClarifyRequest?: (job: JobTarget) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function JobAnalysisModal({
  job,
  open,
  onClose,
  onCreateCvRequest,
  onClarifyRequest,
  onToast,
}: JobAnalysisModalProps) {
  const { data: analysisResponse, isLoading, isError, refetch } = useJobAnalysis(
    open && job ? job.id : undefined
  );
  const analyzeMutation = useAnalyzeJob();

  // Filters state
  const [priorityFilter, setPriorityFilter] = useState<"all" | "mandatory" | "preferred">("all");
  const [statusFilter, setStatusFilter] = useState<"all" | CandidateMatchStatus>("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const analysis = analysisResponse?.analysis || job?.analysis_result;
  const isAnalyzing = analyzeMutation.isPending;

  const handleRunAnalysis = async () => {
    if (!job) return;
    try {
      await analyzeMutation.mutateAsync(job.id);
      onToast("Analysis Complete", `Evaluated requirements and candidate evidence for ${job.title}.`, "success");
    } catch {
      onToast("Analysis Failed", "Could not analyze job requirements. Please check backend connection.", "error");
    }
  };

  // Filtered requirements
  const filteredRequirements = useMemo(() => {
    if (!analysis?.requirements) return [];
    return analysis.requirements.filter((item: JobRequirementItem) => {
      // Priority filter
      if (priorityFilter === "mandatory" && !item.is_mandatory) return false;
      if (priorityFilter === "preferred" && item.is_mandatory) return false;

      // Status filter
      if (statusFilter !== "all" && item.candidate_match_status !== statusFilter) return false;

      // Category filter
      if (categoryFilter !== "all" && item.category !== categoryFilter) return false;

      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesText = item.requirement.toLowerCase().includes(query);
        const matchesReason = item.reasoning?.toLowerCase().includes(query) ?? false;
        const matchesEntity = item.matched_entity_name?.toLowerCase().includes(query) ?? false;
        if (!matchesText && !matchesReason && !matchesEntity) return false;
      }

      return true;
    });
  }, [analysis?.requirements, priorityFilter, statusFilter, categoryFilter, searchQuery]);

  // Unique categories in this job's requirements
  const availableCategories = useMemo(() => {
    if (!analysis?.requirements) return [];
    const set = new Set<string>();
    analysis.requirements.forEach((r) => set.add(r.category));
    return Array.from(set).sort();
  }, [analysis?.requirements]);

  if (!job) return null;

  const summary = analysis?.keyword_summary;

  const getStatusBadge = (status: CandidateMatchStatus) => {
    switch (status) {
      case "supported":
        return (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.25rem",
              padding: "0.2rem 0.5rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 600,
              background: "rgba(16, 185, 129, 0.15)",
              color: "var(--color-emerald-400, #34d399)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
            }}
          >
            <CheckCircle size={14} weight="fill" aria-hidden="true" />
            Supported
          </span>
        );
      case "partial":
        return (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.25rem",
              padding: "0.2rem 0.5rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 600,
              background: "rgba(245, 158, 11, 0.15)",
              color: "var(--color-amber-400, #fbbf24)",
              border: "1px solid rgba(245, 158, 11, 0.3)",
            }}
          >
            <WarningCircle size={14} weight="fill" aria-hidden="true" />
            Partial Match
          </span>
        );
      case "unverified":
        return (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.25rem",
              padding: "0.2rem 0.5rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 600,
              background: "rgba(59, 130, 246, 0.15)",
              color: "var(--color-blue-400, #60a5fa)",
              border: "1px solid rgba(59, 130, 246, 0.3)",
            }}
          >
            <Question size={14} weight="bold" aria-hidden="true" />
            Unverified Claim
          </span>
        );
      case "missing":
      default:
        return (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.25rem",
              padding: "0.2rem 0.5rem",
              borderRadius: "9999px",
              fontSize: "0.75rem",
              fontWeight: 600,
              background: "rgba(148, 163, 184, 0.12)",
              color: "var(--fg-muted, #94a3b8)",
              border: "1px solid rgba(148, 163, 184, 0.25)",
            }}
          >
            <XCircle size={14} weight="fill" aria-hidden="true" />
            Missing
          </span>
        );
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Job Intelligence & Requirement Matching"
      description={`${job.title} at ${job.company_name}`}
      footer={
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <Button
            variant="secondary"
            loading={isAnalyzing}
            icon={<ArrowsClockwise size={16} aria-hidden="true" />}
            onClick={handleRunAnalysis}
          >
            Re-Analyze Match
          </Button>

          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
            {onClarifyRequest ? (
              <Button
                variant="secondary"
                icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
                onClick={() => {
                  onClose();
                  onClarifyRequest(job);
                }}
              >
                Clarify & Tailor
              </Button>
            ) : null}
            <Button
              variant="primary"
              icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
              onClick={() => {
                onClose();
                onCreateCvRequest(job);
              }}
            >
              Create Targeted CV
            </Button>
          </div>
        </div>
      }
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", minHeight: "420px" }}>
        {/* Top Overview & Role Badges */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.5rem",
            alignItems: "center",
            padding: "0.75rem 1rem",
            borderRadius: "0.5rem",
            background: "var(--surface-sunken, rgba(255, 255, 255, 0.03))",
            border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
          }}
        >
          <span style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--fg-default, #fff)", marginRight: "0.5rem" }}>
            {job.company_name}
          </span>
          {analysis?.seniority_level ? (
            <Badge tone="indigo">{analysis.seniority_level}</Badge>
          ) : null}
          {job.employment_type || analysis?.employment_type ? (
            <Badge tone="blue">{job.employment_type || analysis?.employment_type}</Badge>
          ) : null}
          {job.location ? <Badge tone="neutral">{job.location}</Badge> : null}
          <div style={{ marginLeft: "auto", fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)" }}>
            {analysis?.extracted_at ? `Analyzed on ${new Date(analysis.extracted_at).toLocaleDateString()}` : "Ready"}
          </div>
        </div>

        {/* Coverage Scorecards */}
        {summary ? (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
              gap: "0.75rem",
            }}
          >
            {/* Overall Coverage */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "var(--surface-sunken, rgba(255, 255, 255, 0.04))",
                border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", fontWeight: 600 }}>
                Total Match
              </div>
              <div
                style={{
                  fontSize: "1.75rem",
                  fontWeight: 700,
                  color:
                    summary.coverage_percentage >= 70
                      ? "var(--color-emerald-400, #34d399)"
                      : summary.coverage_percentage >= 40
                      ? "var(--color-amber-400, #fbbf24)"
                      : "var(--color-rose-400, #f87171)",
                  marginTop: "0.25rem",
                }}
              >
                {Math.round(summary.coverage_percentage)}%
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                of {summary.total_requirements} requirements
              </div>
            </div>

            {/* Mandatory Coverage */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "var(--surface-sunken, rgba(255, 255, 255, 0.04))",
                border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", fontWeight: 600 }}>
                Must-Haves
              </div>
              <div
                style={{
                  fontSize: "1.75rem",
                  fontWeight: 700,
                  color:
                    summary.mandatory_coverage_percentage >= 70
                      ? "var(--color-emerald-400, #34d399)"
                      : summary.mandatory_coverage_percentage >= 40
                      ? "var(--color-amber-400, #fbbf24)"
                      : "var(--color-rose-400, #f87171)",
                  marginTop: "0.25rem",
                }}
              >
                {Math.round(summary.mandatory_coverage_percentage)}%
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                of {summary.mandatory_count} mandatory
              </div>
            </div>

            {/* Supported count */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "rgba(16, 185, 129, 0.08)",
                border: "1px solid rgba(16, 185, 129, 0.2)",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--color-emerald-400, #34d399)", textTransform: "uppercase", fontWeight: 600 }}>
                Supported
              </div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--color-emerald-400, #34d399)", marginTop: "0.25rem" }}>
                {summary.supported_count}
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                evidence verified
              </div>
            </div>

            {/* Partial count */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "rgba(245, 158, 11, 0.08)",
                border: "1px solid rgba(245, 158, 11, 0.2)",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--color-amber-400, #fbbf24)", textTransform: "uppercase", fontWeight: 600 }}>
                Partial
              </div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--color-amber-400, #fbbf24)", marginTop: "0.25rem" }}>
                {summary.partial_count}
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                related experience
              </div>
            </div>

            {/* Unverified count */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "rgba(59, 130, 246, 0.08)",
                border: "1px solid rgba(59, 130, 246, 0.2)",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--color-blue-400, #60a5fa)", textTransform: "uppercase", fontWeight: 600 }}>
                Unverified
              </div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--color-blue-400, #60a5fa)", marginTop: "0.25rem" }}>
                {summary.unverified_count}
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                claimed in profile
              </div>
            </div>

            {/* Missing count */}
            <div
              style={{
                padding: "0.875rem",
                borderRadius: "0.5rem",
                background: "var(--surface-sunken, rgba(255, 255, 255, 0.04))",
                border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                textAlign: "center",
              }}
            >
              <div style={{ fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", fontWeight: 600 }}>
                Missing
              </div>
              <div style={{ fontSize: "1.75rem", fontWeight: 700, color: "var(--fg-secondary, #d4d4d8)", marginTop: "0.25rem" }}>
                {summary.missing_count}
              </div>
              <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.15rem" }}>
                unaddressed gaps
              </div>
            </div>
          </div>
        ) : null}

        {/* Filter and Search Bar */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.75rem",
            alignItems: "center",
            padding: "0.75rem",
            borderRadius: "0.5rem",
            background: "var(--surface-sunken, rgba(255, 255, 255, 0.02))",
            border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.06))",
          }}
        >
          {/* Search Input */}
          <div style={{ position: "relative", flex: "1 1 200px" }}>
            <MagnifyingGlass
              size={15}
              style={{ position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--fg-muted)" }}
            />
            <input
              type="text"
              placeholder="Search requirements or skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: "100%",
                padding: "0.45rem 0.75rem 0.45rem 2.25rem",
                fontSize: "0.85rem",
                borderRadius: "0.375rem",
                background: "var(--surface-base, rgba(0, 0, 0, 0.3))",
                border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.12))",
                color: "var(--fg-default, #fff)",
                outline: "none",
              }}
            />
          </div>

          {/* Priority Filter */}
          <div style={{ display: "inline-flex", borderRadius: "0.375rem", border: "1px solid var(--border-subtle)", overflow: "hidden" }}>
            {(["all", "mandatory", "preferred"] as const).map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPriorityFilter(p)}
                style={{
                  padding: "0.35rem 0.65rem",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  border: "none",
                  background: priorityFilter === p ? "var(--accent-blue, #3b82f6)" : "transparent",
                  color: priorityFilter === p ? "#fff" : "var(--fg-muted)",
                  cursor: "pointer",
                }}
              >
                {p === "all" ? "All" : p === "mandatory" ? "Required" : "Preferred"}
              </button>
            ))}
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as CandidateMatchStatus | "all")}
            style={{
              padding: "0.35rem 0.65rem",
              fontSize: "0.75rem",
              borderRadius: "0.375rem",
              background: "var(--surface-base, rgba(0, 0, 0, 0.3))",
              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.12))",
              color: "var(--fg-default, #fff)",
              cursor: "pointer",
            }}
          >
            <option value="all">All Match Statuses</option>
            <option value="supported">Supported Only</option>
            <option value="partial">Partial Match Only</option>
            <option value="unverified">Unverified Only</option>
            <option value="missing">Missing Only</option>
          </select>

          {/* Category Filter */}
          {availableCategories.length > 0 ? (
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              style={{
                padding: "0.35rem 0.65rem",
                fontSize: "0.75rem",
                borderRadius: "0.375rem",
                background: "var(--surface-base, rgba(0, 0, 0, 0.3))",
                border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.12))",
                color: "var(--fg-default, #fff)",
                cursor: "pointer",
              }}
            >
              <option value="all">All Categories</option>
              {availableCategories.map((c) => (
                <option key={c} value={c}>
                  {c.charAt(0).toUpperCase() + c.slice(1)}
                </option>
              ))}
            </select>
          ) : null}
        </div>

        {/* Requirements Breakdown List */}
        <div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
            <h3 style={{ fontSize: "0.9rem", fontWeight: 600, color: "var(--fg-default, #fff)", margin: 0 }}>
              Grounded Requirements ({filteredRequirements.length})
            </h3>
            <span style={{ fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)" }}>
              Traceable to candidate Knowledge Base
            </span>
          </div>

          {filteredRequirements.length === 0 ? (
            <div
              style={{
                padding: "2rem",
                textAlign: "center",
                borderRadius: "0.5rem",
                background: "var(--surface-sunken, rgba(0, 0, 0, 0.15))",
                border: "1px dashed var(--border-subtle, rgba(255, 255, 255, 0.1))",
                color: "var(--fg-muted, #a1a1aa)",
                fontSize: "0.875rem",
              }}
            >
              No requirements match your current filters.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", maxHeight: "380px", overflowY: "auto", paddingRight: "0.25rem" }}>
              {filteredRequirements.map((item: JobRequirementItem) => (
                <div
                  key={item.id}
                  style={{
                    padding: "0.875rem 1rem",
                    borderRadius: "0.5rem",
                    background: "var(--surface-sunken, rgba(255, 255, 255, 0.03))",
                    border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.5rem",
                  }}
                >
                  {/* Item Header */}
                  <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.5rem" }}>
                    {getStatusBadge(item.candidate_match_status)}

                    <span
                      style={{
                        padding: "0.15rem 0.45rem",
                        borderRadius: "0.25rem",
                        fontSize: "0.7rem",
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                        background: item.is_mandatory ? "rgba(239, 68, 68, 0.12)" : "rgba(148, 163, 184, 0.12)",
                        color: item.is_mandatory ? "var(--color-rose-400, #f87171)" : "var(--fg-muted, #94a3b8)",
                        border: item.is_mandatory ? "1px solid rgba(239, 68, 68, 0.25)" : "1px solid rgba(148, 163, 184, 0.2)",
                      }}
                    >
                      {item.is_mandatory ? "Required" : "Preferred"}
                    </span>

                    <span
                      style={{
                        padding: "0.15rem 0.45rem",
                        borderRadius: "0.25rem",
                        fontSize: "0.7rem",
                        fontWeight: 500,
                        background: "var(--surface-base, rgba(255, 255, 255, 0.05))",
                        color: "var(--fg-secondary, #d4d4d8)",
                      }}
                    >
                      {item.category}
                    </span>

                    {item.matched_entity_name ? (
                      <span style={{ fontSize: "0.75rem", color: "var(--fg-muted, #a1a1aa)", marginLeft: "auto" }}>
                        Matched: <strong style={{ color: "var(--fg-default, #fff)" }}>{item.matched_entity_name}</strong>
                      </span>
                    ) : null}
                  </div>

                  {/* Requirement Text */}
                  <div style={{ fontSize: "0.9rem", fontWeight: 500, color: "var(--fg-default, #f4f4f5)", lineHeight: 1.5 }}>
                    {item.requirement}
                  </div>

                  {/* Explainable Reasoning */}
                  {item.reasoning ? (
                    <div
                      style={{
                        fontSize: "0.8rem",
                        lineHeight: 1.45,
                        color:
                          item.candidate_match_status === "supported"
                            ? "var(--color-emerald-300, #6ee7b7)"
                            : item.candidate_match_status === "partial"
                            ? "var(--color-amber-300, #fcd34d)"
                            : item.candidate_match_status === "unverified"
                            ? "var(--color-blue-300, #93c5fd)"
                            : "var(--fg-muted, #a1a1aa)",
                        background: "var(--surface-base, rgba(0, 0, 0, 0.2))",
                        padding: "0.45rem 0.75rem",
                        borderRadius: "0.375rem",
                        borderLeft: `3px solid ${
                          item.candidate_match_status === "supported"
                            ? "#10b981"
                            : item.candidate_match_status === "partial"
                            ? "#f59e0b"
                            : item.candidate_match_status === "unverified"
                            ? "#3b82f6"
                            : "#64748b"
                        }`,
                      }}
                    >
                      {item.reasoning}
                    </div>
                  ) : null}

                  {/* Traceable Evidence Items */}
                  {item.evidence_items && item.evidence_items.length > 0 ? (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.25rem", alignItems: "center" }}>
                      <span style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", fontWeight: 600, display: "inline-flex", alignItems: "center", gap: "0.2rem" }}>
                        <ShieldCheck size={13} aria-hidden="true" /> Supporting Evidence:
                      </span>
                      {item.evidence_items.map((ev) => (
                        <div
                          key={ev.id}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "0.35rem",
                            padding: "0.2rem 0.6rem",
                            borderRadius: "0.25rem",
                            background: "rgba(16, 185, 129, 0.1)",
                            border: "1px solid rgba(16, 185, 129, 0.25)",
                            fontSize: "0.75rem",
                            color: "var(--fg-default, #fff)",
                          }}
                        >
                          <span style={{ fontWeight: 600, color: "var(--color-emerald-400, #34d399)" }}>
                            [{ev.source}]
                          </span>
                          <span>{ev.title}</span>
                          {ev.url ? (
                            <a
                              href={ev.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: "var(--accent-blue, #3b82f6)", display: "inline-flex", alignItems: "center" }}
                              title="Open verified evidence link"
                            >
                              <ArrowUpRight size={13} />
                            </a>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Keywords and Identified Gaps Section */}
        {summary && (summary.top_matched_keywords.length > 0 || summary.identified_gaps.length > 0) ? (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: "1rem",
              paddingTop: "0.5rem",
              borderTop: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
            }}
          >
            {/* Matched Keywords */}
            <div>
              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                Top Matched Keywords
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                {summary.top_matched_keywords.map((kw) => (
                  <span
                    key={kw}
                    style={{
                      padding: "0.2rem 0.5rem",
                      borderRadius: "0.25rem",
                      fontSize: "0.75rem",
                      fontWeight: 500,
                      background: "rgba(16, 185, 129, 0.12)",
                      color: "var(--color-emerald-300, #6ee7b7)",
                      border: "1px solid rgba(16, 185, 129, 0.25)",
                    }}
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            {/* Identified Gaps */}
            <div>
              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--fg-muted, #a1a1aa)", textTransform: "uppercase", marginBottom: "0.5rem" }}>
                Identified Actionable Gaps
              </div>
              {summary.identified_gaps.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: "1.2rem", fontSize: "0.775rem", color: "var(--fg-secondary, #d4d4d8)", lineHeight: 1.5 }}>
                  {summary.identified_gaps.slice(0, 4).map((gap, i) => (
                    <li key={i}>{gap}</li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: "0.775rem", color: "var(--color-emerald-400, #34d399)" }}>
                  No major missing gaps detected!
                </div>
              )}
            </div>
          </div>
        ) : null}
      </div>
    </Modal>
  );
}
