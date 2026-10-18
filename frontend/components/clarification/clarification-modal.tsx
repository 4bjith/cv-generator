"use client";

import { useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowsClockwise,
  Check,
  CheckCircle,
  FileText,
  Lightbulb,
  PencilSimple,
  Question,
  ShieldCheck,
  SkipForward,
  Sparkle,
  WarningCircle,
  XCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Card, Modal, ProgressBar, TextareaField } from "@/components/ui";
import {
  useAnswerClarificationQuestion,
  useClarificationSession,
  usePromoteClarification,
  useSkipClarificationQuestion,
  useTailorCv,
} from "@/hooks/use-jobs";
import { ClarificationQuestionItem } from "@/types/clarification";
import { JobTarget } from "@/types/job";
import { CVTailoringResponse } from "@/types/tailoring";

interface ClarificationModalProps {
  job: JobTarget | null;
  open: boolean;
  onClose: () => void;
  onTailoringSuccess: (tailoringResponse: CVTailoringResponse) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function ClarificationModal({
  job,
  open,
  onClose,
  onTailoringSuccess,
  onToast,
}: ClarificationModalProps) {
  const jobId = open && job ? job.id : undefined;

  const { data: session, isLoading, isError, refetch } = useClarificationSession(jobId);
  const answerMutation = useAnswerClarificationQuestion();
  const skipMutation = useSkipClarificationQuestion();
  const promoteMutation = usePromoteClarification();
  const tailorMutation = useTailorCv();

  // Local state for editing answers
  const [draftAnswers, setDraftAnswers] = useState<Record<string, string>>({});
  const [saveToProfileFlags, setSaveToProfileFlags] = useState<Record<string, boolean>>({});
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);

  const questions = session?.questions || [];
  const total = session?.total_questions || 0;
  const answered = session?.answered_count || 0;
  const skipped = session?.skipped_count || 0;
  const progressPercent = total > 0 ? Math.round(((answered + skipped) / total) * 100) : 0;

  const handleSaveAnswer = async (q: ClarificationQuestionItem) => {
    const text = (draftAnswers[q.id] ?? q.answer ?? "").trim();
    if (!text) {
      onToast("Answer Required", "Please provide context or details before saving.", "error");
      return;
    }

    try {
      await answerMutation.mutateAsync({
        jobId: job!.id,
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
    try {
      await skipMutation.mutateAsync({
        jobId: job!.id,
        questionId: q.id,
      });
      onToast("Question Skipped", "Unanswered requirements will remain omitted from factual CV content.", "info");
    } catch {
      onToast("Error", "Could not skip question.", "error");
    }
  };

  const handlePromoteToProfile = async (q: ClarificationQuestionItem) => {
    try {
      await promoteMutation.mutateAsync({
        jobId: job!.id,
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
    if (!job) return;
    try {
      const response = await tailorMutation.mutateAsync({
        jobId: job.id,
        payload: {
          template: "modern",
          tone: "professional",
          include_clarifications: true,
        },
      });
      onToast("CV Tailored Successfully", `Tailored CV snapshot created for ${job.title}.`, "success");
      onClose();
      onTailoringSuccess(response);
    } catch {
      onToast("Tailoring Failed", "Could not generate tailored CV. Please try again.", "error");
    }
  };

  if (!job) return null;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Application Clarification Engine"
      description={`Clarify missing or unverified evidence for ${job.title} at ${job.company_name}`}
      footer={
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8rem", color: "var(--fg-muted, #a1a1aa)" }}>
            <ShieldCheck size={16} color="var(--color-emerald-400, #34d399)" aria-hidden="true" />
            <span>Factual claims only. Unanswered gaps will not be hallucinated.</span>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
              loading={tailorMutation.isPending}
              disabled={tailorMutation.isPending}
              onClick={handleGenerateTailoredCv}
            >
              {tailorMutation.isPending ? "Generating Tailored CV…" : "Generate Tailored CV"}
            </Button>
          </div>
        </div>
      }
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", minHeight: "360px" }}>
        {/* Progress Header */}
        <div
          style={{
            padding: "1rem",
            borderRadius: "0.75rem",
            background: "var(--surface-sunken, rgba(255, 255, 255, 0.03))",
            border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <Lightbulb size={18} color="var(--color-amber-400, #fbbf24)" weight="fill" aria-hidden="true" />
              <span style={{ fontSize: "0.875rem", fontWeight: 600, color: "var(--fg-default, #fff)" }}>
                Clarification Progress
              </span>
            </div>
            <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--fg-muted, #a1a1aa)" }}>
              {answered} of {total} answered ({skipped} skipped)
            </span>
          </div>
          <ProgressBar value={progressPercent} />
        </div>

        {/* Loading State */}
        {isLoading ? (
          <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--fg-muted, #a1a1aa)" }}>
            <ArrowsClockwise size={28} className="animate-spin" style={{ margin: "0 auto 0.75rem auto" }} aria-hidden="true" />
            <p>Analyzing job requirements and identifying prioritized clarification questions…</p>
          </div>
        ) : null}

        {/* Empty State */}
        {!isLoading && questions.length === 0 ? (
          <div
            style={{
              textAlign: "center",
              padding: "2.5rem 1rem",
              background: "rgba(16, 185, 129, 0.08)",
              border: "1px solid rgba(16, 185, 129, 0.2)",
              borderRadius: "0.75rem",
            }}
          >
            <CheckCircle size={32} color="var(--color-emerald-400, #34d399)" weight="fill" style={{ margin: "0 auto 0.5rem auto" }} aria-hidden="true" />
            <h4 style={{ margin: "0 0 0.5rem 0", color: "var(--fg-default, #fff)", fontSize: "1rem" }}>
              All Requirements Verified!
            </h4>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--fg-muted, #a1a1aa)", maxWidth: "440px", marginLeft: "auto", marginRight: "auto" }}>
              Your candidate profile contains sufficient verified evidence for all detected requirements. You can generate a tailored CV immediately.
            </p>
          </div>
        ) : null}

        {/* Questions Stack */}
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {questions.map((q, idx) => {
            const isEditing = editingQuestionId === q.id || q.status === "unanswered";
            const currentAnswer = draftAnswers[q.id] ?? q.answer ?? "";

            return (
              <Card
                key={q.id}
                style={{
                  padding: "1.25rem",
                  border: q.status === "answered"
                    ? "1px solid rgba(16, 185, 129, 0.35)"
                    : q.is_mandatory
                    ? "1px solid rgba(245, 158, 11, 0.3)"
                    : "1px solid var(--border-subtle, rgba(255, 255, 255, 0.1))",
                  background: q.status === "answered"
                    ? "rgba(16, 185, 129, 0.03)"
                    : "var(--surface-default, rgba(255, 255, 255, 0.02))",
                }}
              >
                {/* Header row */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", marginBottom: "0.5rem" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--fg-muted, #71717a)" }}>
                      Q{idx + 1 < 10 ? `0${idx + 1}` : idx + 1}
                    </span>
                    <Badge tone={q.is_mandatory ? "rose" : "neutral"}>
                      {q.is_mandatory ? "Mandatory Gap" : "Preferred"}
                    </Badge>
                    <Badge tone="indigo">{q.category}</Badge>
                    {q.status === "answered" ? (
                      <Badge tone="green">Answered</Badge>
                    ) : q.status === "skipped" ? (
                      <Badge tone="amber">Skipped</Badge>
                    ) : (
                      <Badge tone="amber">Needs Input</Badge>
                    )}
                  </div>

                  {q.status === "answered" ? (
                    <CheckCircle size={20} color="var(--color-emerald-400, #34d399)" weight="fill" aria-label="Answered" />
                  ) : null}
                </div>

                {/* Question Text */}
                <h3 style={{ margin: "0.25rem 0 0.5rem 0", fontSize: "0.95rem", fontWeight: 600, color: "var(--fg-default, #fff)", lineHeight: 1.4 }}>
                  {q.question}
                </h3>

                {/* Context info */}
                <p style={{ margin: "0 0 0.75rem 0", fontSize: "0.8rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.45 }}>
                  {q.context}
                </p>

                {/* Answer Display or Edit Input */}
                {q.status === "answered" && !isEditing ? (
                  <div
                    style={{
                      marginTop: "0.75rem",
                      padding: "0.75rem",
                      borderRadius: "0.5rem",
                      background: "rgba(0, 0, 0, 0.2)",
                      border: "1px solid rgba(255, 255, 255, 0.06)",
                    }}
                  >
                    <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--fg-muted, #71717a)", marginBottom: "0.25rem" }}>
                      Your Answer:
                    </div>
                    <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--fg-default, #fff)", lineHeight: 1.4 }}>
                      {q.answer}
                    </p>

                    <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem", alignItems: "center" }}>
                      <button
                        type="button"
                        onClick={() => setEditingQuestionId(q.id)}
                        style={{
                          background: "none",
                          border: "none",
                          color: "var(--color-blue-400, #60a5fa)",
                          fontSize: "0.775rem",
                          fontWeight: 500,
                          cursor: "pointer",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                        }}
                      >
                        <PencilSimple size={13} aria-hidden="true" /> Edit Answer
                      </button>

                      {!q.save_to_profile ? (
                        <button
                          type="button"
                          onClick={() => handlePromoteToProfile(q)}
                          style={{
                            background: "none",
                            border: "none",
                            color: "var(--color-emerald-400, #34d399)",
                            fontSize: "0.775rem",
                            fontWeight: 500,
                            cursor: "pointer",
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "0.25rem",
                          }}
                        >
                          <ShieldCheck size={13} aria-hidden="true" /> Save to Profile Knowledge Base
                        </button>
                      ) : (
                        <span style={{ fontSize: "0.75rem", color: "var(--color-emerald-400, #34d399)" }}>
                          ✓ Confirmed in Profile
                        </span>
                      )}
                    </div>
                  </div>
                ) : (
                  <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                    <TextareaField
                      label="Your Context / Response"
                      name={`answer-${q.id}`}
                      rows={3}
                      placeholder="Share details, projects, or context demonstrating your experience…"
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
                        fontSize: "0.775rem",
                        color: "var(--fg-secondary, #d4d4d8)",
                        cursor: "pointer",
                        userSelect: "none",
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
                      Save this answer to my permanent career profile knowledge base
                    </label>

                    <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "0.25rem" }}>
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
      </div>
    </Modal>
  );
}
