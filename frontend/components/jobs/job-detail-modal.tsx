"use client";

import { useState } from "react";
import {
  Archive,
  ArrowCounterClockwise,
  ArrowUpRight,
  CalendarBlank,
  MapPin,
  PencilSimple,
  Sparkle,
  Trash,
} from "@phosphor-icons/react";
import { Badge, Button, Modal } from "@/components/ui";
import { useUpdateJob } from "@/hooks/use-jobs";
import { JobTarget } from "@/types/job";

interface JobDetailModalProps {
  job: JobTarget | null;
  open: boolean;
  onClose: () => void;
  onEdit: (job: JobTarget) => void;
  onDeleteRequest: (job: JobTarget) => void;
  onOpenAnalysis?: (job: JobTarget) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function JobDetailModal({
  job,
  open,
  onClose,
  onEdit,
  onDeleteRequest,
  onOpenAnalysis,
  onToast,
}: JobDetailModalProps) {
  const updateMutation = useUpdateJob();
  const [updatingStatus, setUpdatingStatus] = useState(false);

  if (!job) return null;

  const toggleArchiveStatus = async () => {
    try {
      setUpdatingStatus(true);
      const nextStatus = job.status === "saved" ? "archived" : "saved";
      await updateMutation.mutateAsync({
        id: job.id,
        payload: { status: nextStatus },
      });
      onToast(
        nextStatus === "archived" ? "Job Archived" : "Job Restored",
        `${job.title} at ${job.company_name} was marked as ${nextStatus}.`,
        "success"
      );
    } catch {
      onToast("Status Update Failed", "Could not update status. Please try again.", "error");
    } finally {
      setUpdatingStatus(false);
    }
  };

  const formattedCreated = new Date(job.created_at).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  const analysis = job.analysis_result;

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={job.title}
      description={`${job.company_name}${job.location ? ` · ${job.location}` : ""}`}
      footer={
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <Button
            variant="ghost"
            style={{ color: "var(--color-danger, #ef4444)" }}
            icon={<Trash size={16} aria-hidden="true" />}
            onClick={() => {
              onClose();
              onDeleteRequest(job);
            }}
          >
            Delete
          </Button>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <Button
              variant="secondary"
              loading={updatingStatus}
              icon={
                job.status === "saved" ? (
                  <Archive size={16} aria-hidden="true" />
                ) : (
                  <ArrowCounterClockwise size={16} aria-hidden="true" />
                )
              }
              onClick={toggleArchiveStatus}
            >
              {job.status === "saved" ? "Archive" : "Restore"}
            </Button>
            {onOpenAnalysis ? (
              <Button
                variant="secondary"
                icon={<Sparkle size={16} weight="fill" aria-hidden="true" />}
                onClick={() => {
                  onClose();
                  onOpenAnalysis(job);
                }}
              >
                Match Intelligence
              </Button>
            ) : null}
            <Button
              variant="primary"
              icon={<PencilSimple size={16} aria-hidden="true" />}
              onClick={() => {
                onClose();
                onEdit(job);
              }}
            >
              Edit Details
            </Button>
          </div>
        </div>
      }
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Meta Bar */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.75rem",
            alignItems: "center",
            paddingBottom: "1rem",
            borderBottom: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.1))",
          }}
        >
          <Badge tone={job.status === "saved" ? "green" : "neutral"}>
            {job.status === "saved" ? "Active / Saved" : "Archived"}
          </Badge>

          {job.employment_type ? (
            <Badge tone="blue">{job.employment_type}</Badge>
          ) : null}

          {analysis?.keyword_summary ? (
            <Badge tone={analysis.keyword_summary.coverage_percentage >= 70 ? "green" : "amber"}>
              {Math.round(analysis.keyword_summary.coverage_percentage)}% Match (
              {analysis.keyword_summary.supported_count} Supported)
            </Badge>
          ) : null}

          {job.location ? (
            <span style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)" }}>
              <MapPin size={15} aria-hidden="true" /> {job.location}
            </span>
          ) : null}

          <span style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)" }}>
            <CalendarBlank size={15} aria-hidden="true" /> Added {formattedCreated}
          </span>

          {job.source_url ? (
            <a
              href={job.source_url}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "0.25rem",
                fontSize: "0.875rem",
                color: "var(--accent-blue, #3b82f6)",
                textDecoration: "none",
                fontWeight: 500,
                marginLeft: "auto",
              }}
            >
              Original Posting <ArrowUpRight size={14} aria-hidden="true" />
            </a>
          ) : null}
        </div>

        {/* Private Notes */}
        {job.user_notes ? (
          <div
            style={{
              padding: "0.875rem 1rem",
              borderRadius: "0.5rem",
              background: "var(--surface-sunken, rgba(255, 255, 255, 0.04))",
              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
            }}
          >
            <div style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--fg-muted, #a1a1aa)", marginBottom: "0.25rem", fontWeight: 600 }}>
              Private Notes
            </div>
            <p style={{ margin: 0, fontSize: "0.875rem", whiteSpace: "pre-wrap", color: "var(--fg-default, #f4f4f5)" }}>
              {job.user_notes}
            </p>
          </div>
        ) : null}

        {/* Description Body */}
        <div>
          <h3 style={{ fontSize: "0.95rem", fontWeight: 600, marginBottom: "0.5rem", color: "var(--fg-default, #f4f4f5)" }}>
            Job Description
          </h3>
          <div
            style={{
              padding: "1rem",
              borderRadius: "0.5rem",
              background: "var(--surface-sunken, rgba(0, 0, 0, 0.2))",
              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
              maxHeight: "380px",
              overflowY: "auto",
              whiteSpace: "pre-wrap",
              fontSize: "0.875rem",
              lineHeight: 1.6,
              color: "var(--fg-secondary, #d4d4d8)",
            }}
          >
            {job.job_description}
          </div>
        </div>
      </div>
    </Modal>
  );
}
