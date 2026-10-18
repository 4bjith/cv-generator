"use client";

import { useMemo, useState } from "react";
import {
  Briefcase,
  Copy,
  DownloadSimple,
  Eye,
  FileDoc,
  FilePdf,
  MagnifyingGlass,
  PencilSimple,
  Plus,
  ShieldCheck,
  Sparkle,
  Target,
  Trash,
} from "@phosphor-icons/react";
import { Badge, Button, IconButton, Modal } from "@/components/ui";
import {
  useCoverLetterList,
  useDeleteCoverLetter,
  useDuplicateCoverLetter,
  useExportCoverLetterDocx,
  useExportCoverLetterPdf,
  useGenerateCoverLetter,
} from "@/hooks/use-cover-letter";
import { AppView } from "@/types";
import {
  CoverLetterStatus,
  CoverLetterSummary,
  GenerateCoverLetterRequest,
} from "@/types/cover-letter";
import { CoverLetterEditor } from "./cover-letter-editor";
import { CoverLetterGeneratorModal } from "./cover-letter-generator-modal";

interface CoverLetterViewProps {
  onNavigate?: (view: AppView) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

export function CoverLetterView({ onNavigate, onToast }: CoverLetterViewProps) {
  const [activeTab, setActiveTab] = useState<"all" | CoverLetterStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modals & Active Editor
  const [isGeneratorModalOpen, setIsGeneratorModalOpen] = useState(false);
  const [activeEditorId, setActiveEditorId] = useState<string | null>(null);
  const [letterToDelete, setLetterToDelete] = useState<CoverLetterSummary | null>(null);

  // Queries & Mutations
  const filters = useMemo(() => {
    return {
      status: activeTab === "all" ? undefined : activeTab,
      search: searchQuery.trim() || undefined,
      limit: 50,
    };
  }, [activeTab, searchQuery]);

  const { data, isLoading, isError, error, refetch } = useCoverLetterList(filters);
  const generateMutation = useGenerateCoverLetter();
  const duplicateMutation = useDuplicateCoverLetter();
  const deleteMutation = useDeleteCoverLetter();
  const exportPdfMutation = useExportCoverLetterPdf();
  const exportDocxMutation = useExportCoverLetterDocx();

  const letters = data?.items || [];
  const totalCount = data?.total ?? 0;

  const handleGenerate = async (payload: GenerateCoverLetterRequest) => {
    try {
      const created = await generateMutation.mutateAsync(payload);
      setIsGeneratorModalOpen(false);
      onToast(
        "Cover Letter Generated",
        `Created "${created.name}" grounded in verified candidate evidence.`,
        "success"
      );
      // Immediately open editor for review
      setActiveEditorId(created.id);
    } catch (err: any) {
      onToast("Generation Failed", err?.message || "Failed to generate cover letter.", "error");
    }
  };

  const handleDuplicate = async (letter: CoverLetterSummary) => {
    try {
      const copy = await duplicateMutation.mutateAsync({ id: letter.id });
      onToast("Cover Letter Duplicated", `Created copy "${copy.name}".`, "success");
    } catch (err: any) {
      onToast("Duplication Failed", err?.message || "Failed to duplicate cover letter.", "error");
    }
  };

  const handleDelete = async () => {
    if (!letterToDelete) return;
    try {
      await deleteMutation.mutateAsync(letterToDelete.id);
      onToast("Cover Letter Deleted", `"${letterToDelete.name}" has been removed.`, "info");
      setLetterToDelete(null);
    } catch (err: any) {
      onToast("Deletion Failed", err?.message || "Failed to delete cover letter.", "error");
    }
  };

  const handleExportPdf = async (letter: CoverLetterSummary) => {
    try {
      await exportPdfMutation.mutateAsync(letter.id);
      onToast("PDF Exported", `"${letter.name}" downloaded as PDF.`, "success");
    } catch (err: any) {
      onToast("Export Failed", err?.message || "Failed to export PDF.", "error");
    }
  };

  const handleExportDocx = async (letter: CoverLetterSummary) => {
    try {
      await exportDocxMutation.mutateAsync(letter.id);
      onToast("DOCX Exported", `"${letter.name}" downloaded as DOCX.`, "success");
    } catch (err: any) {
      onToast("Export Failed", err?.message || "Failed to export DOCX.", "error");
    }
  };

  // If editing a letter, render the full-screen editor
  if (activeEditorId) {
    return (
      <CoverLetterEditor
        letterId={activeEditorId}
        onClose={() => setActiveEditorId(null)}
        onToast={onToast}
        onNavigateToLetter={(id) => setActiveEditorId(id)}
      />
    );
  }

  return (
    <div className="workspace-container">
      {/* View Header */}
      <div className="section-head" style={{ marginBottom: "1.5rem" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <h1 className="view-title" style={{ margin: 0 }}>
              Cover Letters
            </h1>
            <Badge tone="blue">{totalCount}</Badge>
          </div>
          <p className="view-subtitle" style={{ margin: "0.35rem 0 0 0" }}>
            Tailor evidence-grounded cover letters to your saved job targets, strictly verified against your master Candidate Profile.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {onNavigate && (
            <Button variant="ghost" size="sm" onClick={() => onNavigate("add-job")}>
              View Saved Jobs
            </Button>
          )}
          <Button
            variant="primary"
            size="sm"
            icon={<Sparkle size={16} weight="fill" />}
            onClick={() => setIsGeneratorModalOpen(true)}
          >
            New Cover Letter
          </Button>
        </div>
      </div>

      {/* Grounding Guarantee Banner */}
      <div style={{
        padding: "0.875rem 1.25rem",
        borderRadius: "var(--radius)",
        background: "rgba(16, 185, 129, 0.08)",
        border: "1px solid rgba(16, 185, 129, 0.2)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "0.75rem",
        marginBottom: "1.25rem",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <ShieldCheck size={24} weight="fill" style={{ color: "#059669", flexShrink: 0 }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.875rem", color: "#065f46" }}>
              Zero-Hallucination Evidence Grounding
            </div>
            <div style={{ fontSize: "0.775rem", color: "#047857" }}>
              Cover letters strictly cite verified achievements, metrics, and dates from your profile. Missing requirements are flagged in the truth audit rather than fabricated.
            </div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div
        className="job-filters-bar"
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: "1rem",
          flexWrap: "wrap",
          marginBottom: "1.25rem",
        }}
      >
        {/* Status Tabs */}
        <div className="job-tabs" role="tablist" aria-label="Cover letter status filters">
          <button
            role="tab"
            aria-selected={activeTab === "all"}
            className={`job-tab ${activeTab === "all" ? "job-tab-active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            All
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "draft"}
            className={`job-tab ${activeTab === "draft" ? "job-tab-active" : ""}`}
            onClick={() => setActiveTab("draft")}
          >
            Drafts
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "ready"}
            className={`job-tab ${activeTab === "ready" ? "job-tab-active" : ""}`}
            onClick={() => setActiveTab("ready")}
          >
            Ready
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "archived"}
            className={`job-tab ${activeTab === "archived" ? "job-tab-active" : ""}`}
            onClick={() => setActiveTab("archived")}
          >
            Archived
          </button>
        </div>

        {/* Search Bar */}
        <div className="job-search-input" style={{ position: "relative", minWidth: "260px" }}>
          <MagnifyingGlass
            size={16}
            style={{
              position: "absolute",
              left: "10px",
              top: "50%",
              transform: "translateY(-50%)",
              color: "var(--muted)",
            }}
          />
          <input
            type="search"
            aria-label="Search cover letters"
            placeholder="Search letters by name or job…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem 0.75rem 0.5rem 2rem",
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              fontSize: "0.875rem",
              color: "inherit",
            }}
          />
        </div>
      </div>

      {/* Content Area */}
      {isLoading ? (
        <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--muted)" }}>
          Loading your cover letters...
        </div>
      ) : isError ? (
        <div style={{ textAlign: "center", padding: "3rem 1rem", color: "#ef4444" }}>
          <p>Failed to load cover letters.</p>
          <Button variant="ghost" size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      ) : letters.length === 0 ? (
        <div
          style={{
            textAlign: "center",
            padding: "4rem 2rem",
            background: "var(--card)",
            borderRadius: "var(--radius)",
            border: "1px dashed var(--border)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "1rem",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              background: "rgba(37, 99, 235, 0.08)",
              color: "var(--accent)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Sparkle size={24} weight="fill" />
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 600 }}>
              {searchQuery ? "No matching cover letters found" : "No cover letters yet"}
            </h3>
            <p style={{ margin: "0.35rem 0 0 0", fontSize: "0.875rem", color: "var(--muted)", maxWidth: "440px" }}>
              {searchQuery
                ? `No letters match your search query "${searchQuery}".`
                : "Create your first evidence-grounded cover letter tailored to a saved job target."}
            </p>
          </div>
          {!searchQuery && (
            <Button
              variant="primary"
              size="md"
              icon={<Sparkle size={16} weight="fill" />}
              onClick={() => setIsGeneratorModalOpen(true)}
            >
              Generate First Cover Letter
            </Button>
          )}
        </div>
      ) : (
        /* Letters Grid */
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: "1.25rem",
          }}
        >
          {letters.map((letter) => {
            const formattedDate = new Date(letter.updated_at).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            });

            return (
              <div
                key={letter.id}
                style={{
                  background: "var(--card)",
                  borderRadius: "var(--radius)",
                  border: "1px solid var(--border)",
                  padding: "1.25rem",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "1rem",
                  transition: "box-shadow 0.2s ease, border-color 0.2s ease",
                }}
              >
                {/* Card Top */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                    <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600, lineHeight: 1.3 }}>
                      {letter.name}
                    </h3>
                    <Badge tone={letter.status === "ready" ? "green" : letter.status === "draft" ? "blue" : "neutral"}>
                      {letter.status.toUpperCase()}
                    </Badge>
                  </div>

                  {/* Job Target association */}
                  <div style={{ marginTop: "0.625rem", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.825rem", color: "var(--muted)" }}>
                    <Briefcase size={14} />
                    <span>
                      {letter.job_target_title ? (
                        <strong>
                          {letter.job_target_title}
                          {letter.job_target_company ? ` at ${letter.job_target_company}` : ""}
                        </strong>
                      ) : (
                        "General Position"
                      )}
                    </span>
                  </div>

                  {/* Contextual CV Version */}
                  {letter.cv_version_name && (
                    <div style={{ marginTop: "0.25rem", display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.775rem", color: "var(--muted)" }}>
                      <Target size={14} />
                      <span>Context: {letter.cv_version_name}</span>
                    </div>
                  )}

                  {/* Metadata Tags */}
                  <div style={{ marginTop: "0.75rem", display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
                    <Badge tone="neutral">{letter.tone}</Badge>
                    <Badge tone="neutral">{letter.length_option}</Badge>
                    <Badge tone="neutral">{letter.word_count} words</Badge>
                  </div>
                </div>

                {/* Card Bottom / Actions */}
                <div
                  style={{
                    borderTop: "1px solid var(--border)",
                    paddingTop: "0.875rem",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
                    Updated {formattedDate}
                  </span>

                  <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                    <IconButton
                      label="Export PDF"
                      onClick={() => handleExportPdf(letter)}
                    >
                      <FilePdf size={16} />
                    </IconButton>

                    <IconButton
                      label="Export DOCX"
                      onClick={() => handleExportDocx(letter)}
                    >
                      <FileDoc size={16} />
                    </IconButton>

                    <IconButton
                      label="Duplicate"
                      onClick={() => handleDuplicate(letter)}
                    >
                      <Copy size={16} />
                    </IconButton>

                    <IconButton
                      label="Delete"
                      onClick={() => setLetterToDelete(letter)}
                    >
                      <Trash size={16} />
                    </IconButton>

                    <Button
                      variant="primary"
                      size="sm"
                      icon={<PencilSimple size={14} />}
                      onClick={() => setActiveEditorId(letter.id)}
                    >
                      Edit
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Generator Modal */}
      {isGeneratorModalOpen && (
        <CoverLetterGeneratorModal
          isOpen={isGeneratorModalOpen}
          onClose={() => setIsGeneratorModalOpen(false)}
          onGenerate={handleGenerate}
          isLoading={generateMutation.isPending}
        />
      )}

      {/* Delete Confirmation Modal */}
      {letterToDelete && (
        <Modal
          open={Boolean(letterToDelete)}
          onClose={() => setLetterToDelete(null)}
          title="Delete Cover Letter"
        >
          <p style={{ fontSize: "0.875rem", color: "var(--muted)", margin: 0 }}>
            Are you sure you want to permanently delete <strong>&quot;{letterToDelete.name}&quot;</strong>? This action cannot be undone.
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", marginTop: "1.25rem" }}>
            <Button variant="ghost" onClick={() => setLetterToDelete(null)}>
              Cancel
            </Button>
            <Button
              variant="danger"
              loading={deleteMutation.isPending}
              onClick={handleDelete}
            >
              Delete
            </Button>
          </div>
        </Modal>
      )}
    </div>
  );
}
