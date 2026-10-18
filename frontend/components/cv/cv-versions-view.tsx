"use client";

import { useMemo, useState } from "react";
import {
  Archive,
  ArrowCounterClockwise,
  Copy,
  Eye,
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
  useArchiveCvVersion,
  useCvDetail,
  useCvList,
  useDeleteCvVersion,
  useDuplicateCvVersion,
  useRestoreCvVersion,
} from "@/hooks/use-cv";
import { CVVersion, CVVersionStatus, CVVersionSummary } from "@/types/cv";
import { AppView } from "@/types";
import { CVVersionModal } from "./cv-version-modal";
import { CVSnapshotModal } from "./cv-snapshot-modal";
import { CVVersionEditor } from "./cv-version-editor";

interface CVVersionsViewProps {
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
  onNavigate?: (view: AppView) => void;
}

export function CVVersionsView({ onToast, onNavigate }: CVVersionsViewProps) {
  const [activeTab, setActiveTab] = useState<"all" | CVVersionStatus>("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Modal states
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [inspectingVersionId, setInspectingVersionId] = useState<string | null>(null);
  const [editingVersionId, setEditingVersionId] = useState<string | null>(null);
  const [versionToDelete, setVersionToDelete] = useState<CVVersionSummary | null>(null);

  // Queries & Mutations
  const filterParams = useMemo(() => {
    return {
      status: activeTab === "all" ? undefined : activeTab,
      search: searchQuery.trim() || undefined,
      limit: 50,
    };
  }, [activeTab, searchQuery]);

  const { data, isLoading, isError, error, refetch } = useCvList(filterParams);
  const { data: fullVersionData } = useCvDetail(inspectingVersionId || undefined);

  const duplicateMutation = useDuplicateCvVersion();
  const archiveMutation = useArchiveCvVersion();
  const restoreMutation = useRestoreCvVersion();
  const deleteMutation = useDeleteCvVersion();

  const handleDuplicate = async (v: CVVersionSummary) => {
    try {
      await duplicateMutation.mutateAsync({ id: v.id, payload: {} });
      onToast("CV Version Duplicated", `Created a copy of "${v.name}".`, "success");
    } catch (err: any) {
      onToast("Duplication Failed", err?.message || "Failed to duplicate CV version.", "error");
    }
  };

  const handleArchive = async (v: CVVersionSummary) => {
    try {
      await archiveMutation.mutateAsync(v.id);
      onToast("Version Archived", `"${v.name}" moved to archives.`, "info");
    } catch (err: any) {
      onToast("Archive Failed", err?.message || "Failed to archive version.", "error");
    }
  };

  const handleRestore = async (v: CVVersionSummary) => {
    try {
      await restoreMutation.mutateAsync(v.id);
      onToast("Version Restored", `"${v.name}" restored to drafts.`, "success");
    } catch (err: any) {
      onToast("Restore Failed", err?.message || "Failed to restore version.", "error");
    }
  };

  const handleDelete = async () => {
    if (!versionToDelete) return;
    try {
      await deleteMutation.mutateAsync(versionToDelete.id);
      onToast("Version Deleted", `"${versionToDelete.name}" has been permanently removed.`, "info");
      setVersionToDelete(null);
    } catch (err: any) {
      onToast("Deletion Failed", err?.message || "Failed to delete CV version.", "error");
    }
  };

  const versions = data?.items || [];
  const totalCount = data?.total ?? 0;

  if (editingVersionId) {
    return (
      <CVVersionEditor
        versionId={editingVersionId}
        onClose={() => setEditingVersionId(null)}
        onToast={onToast}
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
              CV Versions & Snapshots
            </h1>
            <Badge tone="blue">{totalCount}</Badge>
          </div>
          <p className="view-subtitle" style={{ margin: "0.35rem 0 0 0" }}>
            Create and manage independently frozen CV point-in-time snapshots derived from your Candidate Profile.
          </p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          {onNavigate && (
            <Button variant="ghost" size="sm" onClick={() => onNavigate("profile")}>
              View Candidate Profile
            </Button>
          )}
          <Button
            variant="primary"
            size="sm"
            icon={<Plus size={16} weight="bold" aria-hidden="true" />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            New CV Version
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="job-filters-bar" style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
        {/* Status Tabs */}
        <div className="job-tabs" role="tablist" aria-label="CV status filters">
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
            style={{ position: "absolute", left: "10px", top: "50%", transform: "translateY(-50%)", color: "var(--color-text-tertiary)" }}
          />
          <input
            type="search"
            aria-label="Search CV versions"
            placeholder="Search versions by name…"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "0.5rem 0.75rem 0.5rem 2rem",
              background: "var(--color-surface)",
              border: "1px solid var(--color-border)",
              borderRadius: "6px",
              color: "var(--color-text-primary)",
              fontSize: "0.85rem",
            }}
          />
        </div>
      </div>

      {/* Error State */}
      {isError && (
        <div
          style={{
            padding: "1rem",
            background: "rgba(239, 68, 68, 0.1)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "8px",
            marginBottom: "1.5rem",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span style={{ color: "var(--color-danger, #ef4444)", fontSize: "0.85rem" }}>
            Failed to load CV versions: {error?.message || "Unknown error"}
          </span>
          <Button size="sm" variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {/* Loading Skeletons */}
      {isLoading && (
        <div className="job-grid" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem" }}>
          {[1, 2, 3].map((n) => (
            <div
              key={n}
              style={{
                height: "170px",
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "10px",
                padding: "1.25rem",
                animation: "pulse 1.5s infinite",
              }}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !isError && versions.length === 0 && (
        <div
          style={{
            padding: "3.5rem 1.5rem",
            background: "var(--color-surface)",
            border: "1px dashed var(--color-border)",
            borderRadius: "12px",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "0.85rem",
          }}
        >
          <div
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "50%",
              background: "rgba(99, 102, 241, 0.1)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "var(--color-primary-500)",
            }}
          >
            <Sparkle size={24} weight="fill" />
          </div>
          <h3 style={{ margin: 0, fontSize: "1.1rem" }}>
            {searchQuery ? "No matching CV versions found" : "No CV versions yet"}
          </h3>
          <p style={{ margin: 0, color: "var(--color-text-secondary)", fontSize: "0.85rem", maxWidth: "420px" }}>
            {searchQuery
              ? `No versions matched "${searchQuery}". Try adjusting your search or clearing filters.`
              : "Freeze an independent point-in-time snapshot of your Candidate Profile to target specific roles."}
          </p>
          {!searchQuery && (
            <Button
              variant="primary"
              size="sm"
              icon={<Plus size={16} weight="bold" />}
              onClick={() => setIsCreateModalOpen(true)}
              style={{ marginTop: "0.5rem" }}
            >
              Generate First CV Version
            </Button>
          )}
        </div>
      )}

      {/* Version Cards Grid */}
      {!isLoading && !isError && versions.length > 0 && (
        <div
          className="job-grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "1rem",
          }}
        >
          {versions.map((v) => (
            <div
              key={v.id}
              style={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "10px",
                padding: "1.25rem",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "1rem",
                boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                transition: "all 0.15s ease",
              }}
            >
              {/* Card Header */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem", marginBottom: "0.4rem" }}>
                  <h3 style={{ margin: 0, fontSize: "1rem", fontWeight: 600, color: "var(--color-text-primary)" }}>
                    {v.name}
                  </h3>
                  <Badge tone={v.status === "ready" ? "success" : v.status === "archived" ? "neutral" : "blue"}>
                    {v.status}
                  </Badge>
                </div>

                {/* Linked Job Target */}
                {v.job_target_title ? (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.4rem",
                      fontSize: "0.82rem",
                      color: "var(--color-primary-500)",
                      fontWeight: 500,
                      marginTop: "0.25rem",
                    }}
                  >
                    <Target size={15} weight="bold" />
                    <span>
                      {v.job_target_company} — {v.job_target_title}
                    </span>
                  </div>
                ) : (
                  <div style={{ fontSize: "0.8rem", color: "var(--color-text-tertiary)", marginTop: "0.25rem" }}>
                    General Master Snapshot
                  </div>
                )}
              </div>

              {/* Timestamp & Info */}
              <div style={{ fontSize: "0.78rem", color: "var(--color-text-tertiary)", display: "flex", justifyContent: "space-between" }}>
                <span>Created {new Date(v.created_at).toLocaleDateString()}</span>
                <span>Snapshot Isolated</span>
              </div>

              {/* Actions Toolbar */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  borderTop: "1px solid var(--color-border)",
                  paddingTop: "0.75rem",
                }}
              >
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Button
                    size="sm"
                    variant="primary"
                    icon={<PencilSimple size={14} />}
                    onClick={() => setEditingVersionId(v.id)}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    icon={<Eye size={14} />}
                    onClick={() => setInspectingVersionId(v.id)}
                  >
                    Inspect
                  </Button>
                  {onNavigate && (
                    <Button
                      size="sm"
                      variant="quiet"
                      icon={<ShieldCheck size={14} />}
                      onClick={() => onNavigate("ats-analysis")}
                      title="Analyze ATS Score & Optimization"
                    >
                      ATS
                    </Button>
                  )}
                </div>

                <div style={{ display: "flex", gap: "0.25rem" }}>
                  <IconButton
                    label="Duplicate version"
                    onClick={() => handleDuplicate(v)}
                    disabled={duplicateMutation.isPending}
                  >
                    <Copy size={16} />
                  </IconButton>

                  {v.status === "archived" ? (
                    <IconButton
                      label="Restore version"
                      onClick={() => handleRestore(v)}
                      disabled={restoreMutation.isPending}
                    >
                      <ArrowCounterClockwise size={16} />
                    </IconButton>
                  ) : (
                    <IconButton
                      label="Archive version"
                      onClick={() => handleArchive(v)}
                      disabled={archiveMutation.isPending}
                    >
                      <Archive size={16} />
                    </IconButton>
                  )}

                  <IconButton
                    label="Delete version"
                    onClick={() => setVersionToDelete(v)}
                  >
                    <Trash size={16} />
                  </IconButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Version Modal */}
      <CVVersionModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onToast={onToast}
      />

      {/* Inspect Snapshot Modal */}
      <CVSnapshotModal
        open={Boolean(inspectingVersionId)}
        onClose={() => setInspectingVersionId(null)}
        version={fullVersionData || null}
      />

      {/* Delete Confirmation Dialog */}
      <Modal
        open={Boolean(versionToDelete)}
        onClose={() => setVersionToDelete(null)}
        title="Delete CV Version?"
        description="Are you sure you want to delete this CV version? This action cannot be undone."
      >
        <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: "1.25rem" }}>
          Version: <strong>{versionToDelete?.name}</strong>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
          <Button variant="ghost" onClick={() => setVersionToDelete(null)}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={handleDelete}
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? "Deleting..." : "Confirm Delete"}
          </Button>
        </div>
      </Modal>
    </div>
  );
}
