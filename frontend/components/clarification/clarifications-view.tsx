"use client";

import { useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowsClockwise,
  Briefcase,
  Check,
  CheckCircle,
  Lightbulb,
  PencilSimple,
  Question,
  ShieldCheck,
  SkipForward,
  Sparkle,
  WarningCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Card, ProgressBar, TextareaField } from "@/components/ui";
import {
  useAnswerClarificationQuestion,
  useClarificationSession,
  useJobList,
  usePromoteClarification,
  useSkipClarificationQuestion,
  useTailorCv,
} from "@/hooks/use-jobs";
import { AppView } from "@/types";
import { ClarificationQuestionItem } from "@/types/clarification";
import { JobTarget } from "@/types/job";
import { CVTailoringResponse } from "@/types/tailoring";
import { TailoringResultModal } from "./tailoring-result-modal";

interface ClarificationsViewProps {
  initialJobId?: string;
  onNavigate: (view: AppView) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onSelectCvVersion?: (versionId: string) => void;
}

export function ClarificationsView({
  initialJobId,
  onNavigate,
  onToast,
  onSelectCvVersion,
}: ClarificationsViewProps) {
  // Fetch available job targets
  const { data: jobListData, isLoading: isJobsLoading } = useJobList();
  const jobs = jobListData?.items || [];

  const [selectedJobId, setSelectedJobId] = useState<string>(
    initialJobId || (jobs.length > 0 ? jobs[0].id : "")
  );

  const activeJobId = selectedJobId || (jobs.length > 0 ? jobs[0].id : undefined);
  const activeJob = useMemo(
    () => jobs.find((j) => j.id === activeJobId) || null,
    [jobs, activeJobId]
  );

  // Clarification session
  const { data: session, isLoading: isSessionLoading } = useClarificationSession(activeJobId);
  const answerMutation = useAnswerClarificationQuestion();
  const skipMutation = useSkipClarificationQuestion();
  const promoteMutation = usePromoteClarification();
  const tailorMutation = useTailorCv();

  // Local draft state
  const [draftAnswers, setDraftAnswers] = useState<Record<string, string>>({});
  const [saveToProfileFlags, setSaveToProfileFlags] = useState<Record<string, boolean>>({});
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);

  // Tailoring result modal state
  const [tailoringResult, setTailoringResult] = useState<CVTailoringResponse | null>(null);
  const [resultModalOpen, setResultModalOpen] = useState(false);

  const questions = session?.questions || [];
  const total = session?.total_questions || 0;
  const answered = session?.answered_count || 0;
  const skipped = session?.skipped_count || 0;
  const progressPercent = total > 0 ? Math.round(((answered + skipped) / total) * 100) : 0;

  const handleSaveAnswer = async (q: ClarificationQuestionItem) => {
    if (!activeJobId) return;
    const text = (draftAnswers[q.id] ?? q.answer ?? "").trim();
    if (!text) {
      onToast("Answer Required", "Please provide context or details before saving.", "error");
      return;
    }

    try {
      await answerMutation.mutateAsync({
        jobId: activeJobId,
        questionId: q.id,
        payload: {
          answer: text,
          save_to_profile: Boolean(saveToProfileFlags[q.id]),
        },
      });
      setEditingQuestionId(null);
      onToast("Answer Saved", "Response recorded and preserved for CV tailoring.", "success");
    } catch {
      onToast("Error Saving Answer", "Could not persist clarification answer.", "error");
    }
  };

  const handleSkip = async (q: ClarificationQuestionItem) => {
    if (!activeJobId) return;
    try {
      await skipMutation.mutateAsync({
        jobId: activeJobId,
        questionId: q.id,
      });
      onToast("Question Skipped", "Unanswered requirements will remain omitted from factual CV content.", "info");
    } catch {
      onToast("Error", "Could not skip question.", "error");
    }
  };

  const handlePromoteToProfile = async (q: ClarificationQuestionItem) => {
    if (!activeJobId) return;
    try {
      await promoteMutation.mutateAsync({
        jobId: activeJobId,
        questionId: q.id,
        payload: {
          category: q.category,
          skill_proficiency: "intermediate",
        },
      });
      onToast("Added to Profile", "Claim added to career profile with unverified provenance.", "success");
    } catch {
      onToast("Error", "Could not promote to profile.", "error");
    }
  };

  const handleGenerateTailoredCv = async () => {
    if (!activeJob) return;
    try {
      const response = await tailorMutation.mutateAsync({
        jobId: activeJob.id,
        payload: {
          template: "modern",
          tone: "professional",
          include_clarifications: true,
        },
      });
      onToast("CV Tailored Successfully", `Tailored CV snapshot created for ${activeJob.title}.`, "success");
      setTailoringResult(response);
      setResultModalOpen(true);
    } catch {
      onToast("Tailoring Failed", "Could not generate tailored CV. Please try again.", "error");
    }
  };

  return (
    <div className="page-frame">
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Clarification Engine</span>
          <h1 className="page-title">Application Evidence Clarifications</h1>
          <p className="page-subtitle">
            Address unverified or missing requirements with confirmed facts. Unanswered gaps will not be hallucinated.
          </p>
        </div>
        <div className="page-header-actions" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <Button
            variant="ghost"
            icon={<ArrowLeft size={16} aria-hidden="true" />}
            onClick={() => onNavigate("job-analysis")}
          >
            Back to Job Targets
          </Button>
          <Button
            variant="primary"
            icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
            loading={tailorMutation.isPending}
            disabled={tailorMutation.isPending || !activeJob}
            onClick={handleGenerateTailoredCv}
          >
            {tailorMutation.isPending ? "Generating Tailored CV…" : "Generate Tailored CV"}
          </Button>
        </div>
      </div>

      {/* Target Job Selector Bar */}
      {jobs.length > 1 ? (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.75rem",
            padding: "0.75rem 1rem",
            borderRadius: "0.75rem",
            background: "var(--surface-sunken, rgba(255, 255, 255, 0.03))",
            border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
            marginBottom: "1rem",
          }}
        >
          <Briefcase size={18} color="var(--color-blue-400, #60a5fa)" aria-hidden="true" />
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--fg-default, #fff)" }}>
            Target Opportunity:
          </span>
          <select
            value={activeJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            style={{
              padding: "0.35rem 0.75rem",
              borderRadius: "0.375rem",
              background: "var(--surface-default, #18181b)",
              color: "var(--fg-default, #fff)",
              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.15))",
              fontSize: "0.85rem",
            }}
          >
            {jobs.map((j) => (
              <option key={j.id} value={j.id}>
                {j.title} at {j.company_name}
              </option>
            ))}
          </select>
        </div>
      ) : null}

      {/* Progress & Resumption Banner */}
      <div
        style={{
          padding: "1.25rem",
          borderRadius: "0.75rem",
          background: "var(--surface-sunken, rgba(255, 255, 255, 0.03))",
          border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
          marginBottom: "1.25rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.75rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Lightbulb size={20} color="var(--color-amber-400, #fbbf24)" weight="fill" aria-hidden="true" />
            <div>
              <strong style={{ fontSize: "0.95rem", color: "var(--fg-default, #fff)" }}>
                {activeJob ? `${activeJob.title} · ${activeJob.company_name}` : "Clarification Session"}
              </strong>
              <div style={{ fontSize: "0.775rem", color: "var(--fg-muted, #a1a1aa)" }}>
                Answers are persisted across sessions and applied directly to tailored CV generation.
              </div>
            </div>
          </div>

          <Badge tone="green">
            {answered} of {total} Answered ({skipped} Skipped)
          </Badge>
        </div>
        <ProgressBar value={progressPercent} />
      </div>

      {/* Loading state */}
      {isSessionLoading ? (
        <div style={{ textAlign: "center", padding: "4rem 1rem", color: "var(--fg-muted, #a1a1aa)" }}>
          <ArrowsClockwise size={32} className="animate-spin" style={{ margin: "0 auto 1rem auto" }} aria-hidden="true" />
          <p>Loading prioritized clarification session…</p>
        </div>
      ) : null}

      {/* Empty State */}
      {!isSessionLoading && questions.length === 0 ? (
        <Card style={{ textAlign: "center", padding: "3rem 1.5rem" }}>
          <CheckCircle size={40} color="var(--color-emerald-400, #34d399)" weight="fill" style={{ margin: "0 auto 1rem auto" }} aria-hidden="true" />
          <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--fg-default, #fff)" }}>
            Zero Evidence Gaps Detected
          </h3>
          <p style={{ margin: "0 auto 1.5rem auto", maxWidth: "480px", fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)" }}>
            All detected requirements for this job target are supported by verified evidence in your candidate profile.
          </p>
          <Button
            variant="primary"
            icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
            onClick={handleGenerateTailoredCv}
            loading={tailorMutation.isPending}
          >
            Generate Tailored CV Now
          </Button>
        </Card>
      ) : null}

      {/* Question Cards Stack */}
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {questions.map((q, idx) => {
          const isEditing = editingQuestionId === q.id || q.status === "unanswered";
          const currentAnswer = draftAnswers[q.id] ?? q.answer ?? "";

          return (
            <Card
              key={q.id}
              style={{
                padding: "1.5rem",
                border: q.status === "answered"
                  ? "1px solid rgba(16, 185, 129, 0.3)"
                  : q.is_mandatory
                  ? "1px solid rgba(245, 158, 11, 0.3)"
                  : "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                background: q.status === "answered"
                  ? "rgba(16, 185, 129, 0.03)"
                  : "var(--surface-default, rgba(255, 255, 255, 0.02))",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", marginBottom: "0.75rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--fg-muted, #71717a)" }}>
                    {idx + 1 < 10 ? `0${idx + 1}` : idx + 1}
                  </span>
                  <Badge tone={q.is_mandatory ? "rose" : "neutral"}>
                    {q.is_mandatory ? "Mandatory Requirement Gap" : "Preferred"}
                  </Badge>
                  <Badge tone="indigo">{q.category}</Badge>
                  {q.status === "answered" ? (
                    <Badge tone="green">Answered</Badge>
                  ) : q.status === "skipped" ? (
                    <Badge tone="amber">Skipped</Badge>
                  ) : (
                    <Badge tone="amber">Unanswered</Badge>
                  )}
                </div>

                {q.status === "answered" ? (
                  <CheckCircle size={22} color="var(--color-emerald-400, #34d399)" weight="fill" aria-label="Answered" />
                ) : null}
              </div>

              <h2 style={{ margin: "0.25rem 0 0.5rem 0", fontSize: "1.05rem", fontWeight: 700, color: "var(--fg-default, #fff)", lineHeight: 1.4 }}>
                {q.question}
              </h2>

              <p style={{ margin: "0 0 1rem 0", fontSize: "0.85rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.5 }}>
                {q.context}
              </p>

              {q.status === "answered" && !isEditing ? (
                <div
                  style={{
                    padding: "0.875rem 1rem",
                    borderRadius: "0.5rem",
                    background: "rgba(0, 0, 0, 0.25)",
                    border: "1px solid rgba(255, 255, 255, 0.08)",
                  }}
                >
                  <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--fg-muted, #71717a)", marginBottom: "0.35rem" }}>
                    Your Saved Context:
                  </div>
                  <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--fg-default, #fff)", lineHeight: 1.45 }}>
                    {q.answer}
                  </p>

                  <div style={{ display: "flex", gap: "1rem", marginTop: "0.75rem", alignItems: "center" }}>
                    <button
                      type="button"
                      onClick={() => setEditingQuestionId(q.id)}
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--color-blue-400, #60a5fa)",
                        fontSize: "0.8rem",
                        fontWeight: 600,
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.3rem",
                      }}
                    >
                      <PencilSimple size={14} aria-hidden="true" /> Edit Answer
                    </button>

                    {!q.save_to_profile ? (
                      <button
                        type="button"
                        onClick={() => handlePromoteToProfile(q)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "var(--color-emerald-400, #34d399)",
                          fontSize: "0.8rem",
                          fontWeight: 600,
                          cursor: "pointer",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.3rem",
                        }}
                      >
                        <ShieldCheck size={14} aria-hidden="true" /> Promote to Career Profile
                      </button>
                    ) : (
                      <span style={{ fontSize: "0.8rem", color: "var(--color-emerald-400, #34d399)" }}>
                        ✓ Confirmed in Profile Knowledge Base
                      </span>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  <TextareaField
                    label="Your Context / Response"
                    name={`answer-${q.id}`}
                    rows={3}
                    placeholder="Provide details of your experience, project context, or metrics…"
                    value={currentAnswer}
                    onChange={(e) =>
                      setDraftAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))
                    }
                  />

                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                      fontSize: "0.8rem",
                      color: "var(--fg-secondary, #d4d4d8)",
                      cursor: "pointer",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={Boolean(saveToProfileFlags[q.id])}
                      onChange={(e) =>
                        setSaveToProfileFlags((prev) => ({
                          ...prev,
                          [q.id]: e.target.checked,
                        }))
                      }
                    />
                    Add this confirmed answer to my permanent career profile knowledge base
                  </label>

                  <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "0.5rem" }}>
                    {q.status !== "skipped" ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={<SkipForward size={14} aria-hidden="true" />}
                        onClick={() => handleSkip(q)}
                      >
                        Skip
                      </Button>
                    ) : null}

                    {editingQuestionId === q.id ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingQuestionId(null)}
                      >
                        Cancel
                      </Button>
                    ) : null}

                    <Button
                      variant="secondary"
                      size="sm"
                      icon={<Check size={14} aria-hidden="true" />}
                      loading={answerMutation.isPending}
                      onClick={() => handleSaveAnswer(q)}
                    >
                      Save Answer
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Tailoring Result Modal */}
      <TailoringResultModal
        open={resultModalOpen}
        result={tailoringResult}
        onClose={() => setResultModalOpen(false)}
        onOpenEditor={(versionId) => {
          setResultModalOpen(false);
          if (onSelectCvVersion) {
            onSelectCvVersion(versionId);
          }
          onNavigate("cv-editor");
        }}
        onToast={onToast}
      />
    </div>
  );
}
