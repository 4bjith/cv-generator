"use client";

import { useMemo, useState } from "react";
import {
  Archive,
  ArrowCounterClockwise,
  ArrowUpRight,
  Briefcase,
  Buildings,
  CalendarBlank,
  CaretRight,
  DotsThree,
  Funnel,
  MagnifyingGlass,
  MapPin,
  NotePencil,
  PencilSimple,
  Plus,
  Sparkle,
  Trash,
  WarningCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Card, IconButton, Modal } from "@/components/ui";
import { AppView } from "@/types";
import { JobTarget, JobTargetStatus } from "@/types/job";
import { useDeleteJob, useJobList, useUpdateJob } from "@/hooks/use-jobs";
import { JobTargetModal } from "./job-target-modal";
import { JobDetailModal } from "./job-detail-modal";
import { JobAnalysisModal } from "./job-analysis-modal";
import { CVVersionModal } from "../cv/cv-version-modal";
import { ClarificationModal } from "../clarification/clarification-modal";
import { TailoringResultModal } from "../clarification/tailoring-result-modal";
import { CVTailoringResponse } from "@/types/tailoring";

interface JobTargetsViewProps {
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onNavigate?: (view: AppView) => void;
}

export function JobTargetsView({ onToast, onNavigate }: JobTargetsViewProps) {
  const [statusFilter, setStatusFilter] = useState<"all" | JobTargetStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const [modalOpen, setModalOpen] = useState(false);
  const [jobToEdit, setJobToEdit] = useState<JobTarget | null>(null);

  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<JobTarget | null>(null);

  const [analysisModalOpen, setAnalysisModalOpen] = useState(false);
  const [analysisJob, setAnalysisJob] = useState<JobTarget | null>(null);

  const [targetedCvModalOpen, setTargetedCvModalOpen] = useState(false);
  const [targetedCvJob, setTargetedCvJob] = useState<JobTarget | null>(null);

  const [clarificationModalOpen, setClarificationModalOpen] = useState(false);
  const [clarificationJob, setClarificationJob] = useState<JobTarget | null>(null);
  const [tailoringResult, setTailoringResult] = useState<CVTailoringResponse | null>(null);
  const [tailoringResultModalOpen, setTailoringResultModalOpen] = useState(false);

  const [deleteConfirmJob, setDeleteConfirmJob] = useState<JobTarget | null>(null);

  // TanStack Query Hooks
  const { data, isLoading, isError, refetch } = useJobList({
    status: statusFilter === "all" ? undefined : statusFilter,
    search: searchQuery.trim() || undefined,
  });

  const deleteMutation = useDeleteJob();
  const updateMutation = useUpdateJob();

  const jobs = data?.items || [];
  const total = data?.total || 0;

  // Derive counts
  const savedCount = useMemo(() => jobs.filter((j) => j.status === "saved").length, [jobs]);
  const archivedCount = useMemo(() => jobs.filter((j) => j.status === "archived").length, [jobs]);

  const handleOpenCreate = () => {
    setJobToEdit(null);
    setModalOpen(true);
  };

  const handleOpenEdit = (job: JobTarget) => {
    setJobToEdit(job);
    setModalOpen(true);
  };

  const handleOpenDetail = (job: JobTarget) => {
    setSelectedJob(job);
    setDetailModalOpen(true);
  };

  const handleOpenAnalysis = (job: JobTarget) => {
    setAnalysisJob(job);
    setAnalysisModalOpen(true);
  };

  const handleCreateTargetedCv = (job: JobTarget) => {
    setTargetedCvJob(job);
    setTargetedCvModalOpen(true);
  };

  const handleOpenClarification = (job: JobTarget) => {
    setClarificationJob(job);
    setClarificationModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmJob) return;
    try {
      await deleteMutation.mutateAsync(deleteConfirmJob.id);
      onToast("Job Target Deleted", `${deleteConfirmJob.title} at ${deleteConfirmJob.company_name} was removed.`, "success");
      setDeleteConfirmJob(null);
    } catch {
      onToast("Delete Failed", "Could not delete job target. Please try again.", "error");
    }
  };

  const handleToggleArchive = async (job: JobTarget, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    try {
      const nextStatus: JobTargetStatus = job.status === "saved" ? "archived" : "saved";
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
      onToast("Update Failed", "Could not update status. Please try again.", "error");
    }
  };

  const getCompanyInitials = (name: string) => {
    return (
      name
        .split(" ")
        .filter(Boolean)
        .map((w) => w[0])
        .join("")
        .slice(0, 2)
        .toUpperCase() || "JB"
    );
  };

  return (
    <div className="page-frame">
      {/* Header Bar */}
      <div className="page-header">
        <div>
          <span className="page-eyebrow">Career Pipeline & Targets</span>
          <h1 className="page-title">Job Targets</h1>
          <p className="page-subtitle">
            Capture opportunities, extract structured requirements, and compare grounded evidence for tailored CVs.
          </p>
        </div>
        <div className="page-header-actions">
          <Button
            variant="primary"
            icon={<Plus size={16} aria-hidden="true" />}
            onClick={handleOpenCreate}
            id="add-job-target-btn"
          >
            Add Target Job
          </Button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "1rem",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "1.5rem",
        }}
      >
        {/* Status Filter Tabs */}
        <div style={{ display: "inline-flex", borderRadius: "0.5rem", border: "1px solid var(--border-subtle)", overflow: "hidden" }}>
          <button
            type="button"
            onClick={() => setStatusFilter("all")}
            style={{
              padding: "0.5rem 1rem",
              fontSize: "0.875rem",
              fontWeight: 500,
              border: "none",
              background: statusFilter === "all" ? "var(--accent-blue, #3b82f6)" : "transparent",
              color: statusFilter === "all" ? "#ffffff" : "var(--fg-muted, #a1a1aa)",
              cursor: "pointer",
            }}
          >
            All Jobs ({total})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter("saved")}
            style={{
              padding: "0.5rem 1rem",
              fontSize: "0.875rem",
              fontWeight: 500,
              border: "none",
              borderLeft: "1px solid var(--border-subtle)",
              background: statusFilter === "saved" ? "var(--accent-blue, #3b82f6)" : "transparent",
              color: statusFilter === "saved" ? "#ffffff" : "var(--fg-muted, #a1a1aa)",
              cursor: "pointer",
            }}
          >
            Active Saved ({savedCount})
          </button>
          <button
            type="button"
            onClick={() => setStatusFilter("archived")}
            style={{
              padding: "0.5rem 1rem",
              fontSize: "0.875rem",
              fontWeight: 500,
              border: "none",
              borderLeft: "1px solid var(--border-subtle)",
              background: statusFilter === "archived" ? "var(--accent-blue, #3b82f6)" : "transparent",
              color: statusFilter === "archived" ? "#ffffff" : "var(--fg-muted, #a1a1aa)",
              cursor: "pointer",
            }}
          >
            Archived ({archivedCount})
          </button>
        </div>

        {/* Search Input */}
        <div style={{ position: "relative", minWidth: "260px", flex: "1 1 280px", maxWidth: "420px" }}>
          <MagnifyingGlass
            size={18}
            style={{
              position: "absolute",
              left: "0.75rem",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--fg-muted, #a1a1aa)",
            }}
          />
          <input
            type="text"
            placeholder="Search by title, company, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem 0.75rem 0.5rem 2.25rem",
              fontSize: "0.875rem",
              borderRadius: "0.5rem",
              background: "var(--surface-sunken, rgba(0, 0, 0, 0.2))",
              border: "1px solid var(--border-subtle, rgba(255, 255, 255, 0.1))",
              color: "var(--fg-default, #f4f4f5)",
              outline: "none",
            }}
          />
        </div>
      </div>

      {/* Loading & Error States */}
      {isLoading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {[1, 2, 3].map((i) => (
            <Card key={i} style={{ height: "110px", opacity: 0.5 }} className="animate-pulse">
              <div style={{ height: "100%" }} />
            </Card>
          ))}
        </div>
      ) : isError ? (
        <Card style={{ padding: "2rem", textAlign: "center", color: "var(--fg-muted, #a1a1aa)" }}>
          <WarningCircle size={32} style={{ margin: "0 auto 0.5rem", color: "var(--color-danger, #ef4444)" }} />
          <h3 style={{ margin: "0 0 0.5rem", color: "var(--fg-default, #f4f4f5)" }}>Failed to Load Job Targets</h3>
          <p style={{ margin: "0 0 1rem", fontSize: "0.875rem" }}>
            Could not retrieve target jobs. Please check your network connection or try again.
          </p>
          <Button variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        </Card>
      ) : jobs.length === 0 ? (
        /* Empty State */
        <Card
          style={{
            padding: "3.5rem 2rem",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "var(--surface-sunken, rgba(255, 255, 255, 0.02))",
            border: "1px dashed var(--border-subtle, rgba(255, 255, 255, 0.15))",
          }}
        >
          <div
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "50%",
              background: "rgba(59, 130, 246, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: "1rem",
              color: "var(--accent-blue, #3b82f6)",
            }}
          >
            <Briefcase size={28} />
          </div>
          <h3 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 0.5rem", color: "var(--fg-default, #f4f4f5)" }}>
            {searchQuery.trim() || statusFilter !== "all" ? "No Matching Job Targets" : "No Target Jobs Saved Yet"}
          </h3>
          <p style={{ maxWidth: "460px", margin: "0 0 1.5rem", fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.5 }}>
            {searchQuery.trim() || statusFilter !== "all"
              ? "Try adjusting your search query or status filter to find your saved opportunities."
              : "Paste job descriptions you are actively targeting. The intelligence engine extracts required skills, constraints, and runs evidence-grounded candidate matching."}
          </p>
          {searchQuery.trim() || statusFilter !== "all" ? (
            <Button
              variant="secondary"
              onClick={() => {
                setSearchQuery("");
                setStatusFilter("all");
              }}
            >
              Clear Filters
            </Button>
          ) : (
            <Button variant="primary" icon={<Plus size={16} />} onClick={handleOpenCreate}>
              Add Your First Target Job
            </Button>
          )}
        </Card>
      ) : (
        /* Job Target Cards Grid / List */
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {jobs.map((job) => {
            const formattedDate = new Date(job.created_at).toLocaleDateString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
            });

            const analysisSummary = job.analysis_result?.keyword_summary;

            return (
              <Card
                key={job.id}
                style={{
                  padding: "1.25rem 1.5rem",
                  transition: "all 0.15s ease",
                  cursor: "pointer",
                }}
                className="hover-card"
                onClick={() => handleOpenDetail(job)}
              >
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "1rem",
                  }}
                >
                  {/* Left Identity */}
                  <div style={{ display: "flex", alignItems: "center", gap: "1rem", minWidth: "240px", flex: "1 1 300px" }}>
                    <span className="company-mark company-purple">{getCompanyInitials(job.company_name)}</span>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                        <h3 style={{ fontSize: "1.05rem", fontWeight: 600, margin: 0, color: "var(--fg-default, #f4f4f5)" }}>
                          {job.title}
                        </h3>
                        <Badge tone={job.status === "saved" ? "green" : "neutral"}>
                          {job.status === "saved" ? "Active" : "Archived"}
                        </Badge>
                        {job.employment_type ? (
                          <Badge tone="blue">{job.employment_type}</Badge>
                        ) : null}
                        {analysisSummary ? (
                          <Badge tone={analysisSummary.coverage_percentage >= 70 ? "green" : "amber"}>
                            {Math.round(analysisSummary.coverage_percentage)}% Match
                          </Badge>
                        ) : null}
                      </div>
                      <p style={{ margin: "0.2rem 0 0", fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)" }}>
                        <strong style={{ color: "var(--fg-secondary, #d4d4d8)" }}>{job.company_name}</strong>
                        {job.location ? ` · ${job.location}` : ""}
                      </p>
                    </div>
                  </div>

                  {/* Metadata & Actions */}
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "1rem",
                      flexWrap: "wrap",
                      justifyContent: "flex-end",
                    }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {job.user_notes ? (
                      <span
                        title="Has private notes"
                        style={{
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.3rem",
                          fontSize: "0.8125rem",
                          color: "var(--accent-purple, #a855f7)",
                        }}
                      >
                        <NotePencil size={15} /> Notes
                      </span>
                    ) : null}

                    <span style={{ fontSize: "0.8125rem", color: "var(--fg-muted, #71717a)" }}>
                      <CalendarBlank size={14} style={{ verticalAlign: "middle", marginRight: 4 }} />
                      {formattedDate}
                    </span>

                    {/* Action Buttons */}
                    <div style={{ display: "flex", gap: "0.35rem" }}>
                      <Button
                        variant="secondary"
                        size="sm"
                        icon={<Sparkle size={14} weight="fill" aria-hidden="true" />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenAnalysis(job);
                        }}
                      >
                        {analysisSummary ? "Match Intel" : "Analyze Match"}
                      </Button>

                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenClarification(job);
                        }}
                        title="Clarify missing qualifications and tailor CV"
                      >
                        Clarify & Tailor
                      </Button>

                      <Button
                        variant="quiet"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenDetail(job);
                        }}
                      >
                        View
                      </Button>

                      <Button
                        variant="quiet"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleOpenEdit(job);
                        }}
                      >
                        <PencilSimple size={15} aria-label="Edit job target" />
                      </Button>

                      <Button
                        variant="quiet"
                        size="sm"
                        onClick={(e) => handleToggleArchive(job, e)}
                        title={job.status === "saved" ? "Archive job" : "Restore job"}
                      >
                        {job.status === "saved" ? (
                          <Archive size={15} aria-label="Archive job" />
                        ) : (
                          <ArrowCounterClockwise size={15} aria-label="Restore job" />
                        )}
                      </Button>

                      <Button
                        variant="quiet"
                        size="sm"
                        style={{ color: "var(--color-danger, #ef4444)" }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteConfirmJob(job);
                        }}
                        title="Delete job target"
                      >
                        <Trash size={15} aria-label="Delete job target" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Description Snippet */}
                <p
                  style={{
                    margin: "0.75rem 0 0",
                    fontSize: "0.875rem",
                    color: "var(--fg-muted, #a1a1aa)",
                    lineHeight: 1.5,
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                  }}
                >
                  {job.job_description}
                </p>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create / Edit Modal */}
      <JobTargetModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        jobToEdit={jobToEdit}
        onToast={onToast}
      />

      {/* Detail Modal */}
      <JobDetailModal
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        job={selectedJob}
        onEdit={handleOpenEdit}
        onDeleteRequest={(job) => setDeleteConfirmJob(job)}
        onOpenAnalysis={handleOpenAnalysis}
        onToast={onToast}
      />

      {/* Job Intelligence Analysis Modal */}
      <JobAnalysisModal
        open={analysisModalOpen}
        onClose={() => setAnalysisModalOpen(false)}
        job={analysisJob}
        onCreateCvRequest={handleCreateTargetedCv}
        onClarifyRequest={(job) => {
          setClarificationJob(job);
          setClarificationModalOpen(true);
        }}
        onToast={onToast}
      />

      {/* Targeted CV Creation Modal */}
      <CVVersionModal
        open={targetedCvModalOpen}
        onClose={() => setTargetedCvModalOpen(false)}
        initialJobTargetId={targetedCvJob?.id}
        initialName={targetedCvJob ? `${targetedCvJob.title} - ${targetedCvJob.company_name}` : ""}
        onToast={onToast}
        onSuccess={(_created) => {
          setTargetedCvModalOpen(false);
          if (onNavigate) {
            onNavigate("cv-generation");
          }
        }}
      />

      {/* Clarification Questions Modal */}
      <ClarificationModal
        job={clarificationJob}
        open={clarificationModalOpen}
        onClose={() => setClarificationModalOpen(false)}
        onTailoringSuccess={(res) => {
          setTailoringResult(res);
          setTailoringResultModalOpen(true);
        }}
        onToast={onToast}
      />

      {/* Tailored CV Result & Template Preview Modal */}
      <TailoringResultModal
        open={tailoringResultModalOpen}
        result={tailoringResult}
        onClose={() => setTailoringResultModalOpen(false)}
        onOpenEditor={(_versionId) => {
          setTailoringResultModalOpen(false);
          if (onNavigate) {
            onNavigate("cv-editor");
          }
        }}
        onToast={onToast}
      />

      {/* Delete Confirmation Modal */}
      <Modal
        open={Boolean(deleteConfirmJob)}
        onClose={() => setDeleteConfirmJob(null)}
        title="Delete Job Target?"
        description={`Are you sure you want to permanently delete "${deleteConfirmJob?.title}" at "${deleteConfirmJob?.company_name}"?`}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", width: "100%" }}>
            <Button variant="ghost" onClick={() => setDeleteConfirmJob(null)} disabled={deleteMutation.isPending}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={deleteMutation.isPending}
              icon={<Trash size={16} aria-hidden="true" />}
              onClick={handleDeleteConfirm}
            >
              Delete Job Target
            </Button>
          </div>
        }
      >
        <p style={{ margin: 0, fontSize: "0.875rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.6 }}>
          This will permanently remove the target job opportunity from your workspace.
        </p>
      </Modal>
    </div>
  );
}
