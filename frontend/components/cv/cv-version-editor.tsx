"use client";

import { useEffect, useMemo, useState } from "react";
import {
  ArrowDown,
  ArrowLeft,
  ArrowUp,
  Briefcase,
  Certificate,
  Check,
  Code,
  DownloadSimple,
  Eye,
  EyeSlash,
  FloppyDisk,
  GraduationCap,
  Plus,
  Trash,
  Trophy,
  User,
  Warning,
  X,
} from "@phosphor-icons/react";
import { Badge, Button, IconButton, Modal, Field, TextareaField } from "@/components/ui";
import { useCvDetail, useExportDocx, useExportPdf, useUpdateCvVersion } from "@/hooks/use-cv";
import { cvApi } from "@/services/cv/cv.api";
import {
  CVBasicsSnapshot,
  CVContentSnapshot,
  CVPresentationSnapshot,
  CVWorkSnapshot,
  CVEducationSnapshot,
  CVSkillSnapshot,
  CVProjectSnapshot,
  CVCertificateSnapshot,
  CVAwardSnapshot,
  CVLanguageSnapshot,
} from "@/types/cv";
import { CVRenderer } from "./templates";

interface CVVersionEditorProps {
  versionId: string;
  onClose: () => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const DEFAULT_SECTION_ORDER = [
  "basics",
  "work",
  "skills",
  "projects",
  "education",
  "certificates",
  "awards",
  "languages",
];

const SECTION_METADATA: Record<string, { label: string; icon: any }> = {
  basics: { label: "Personal & Professional Identity", icon: User },
  work: { label: "Work Experience", icon: Briefcase },
  skills: { label: "Skills & Proficiencies", icon: Code },
  projects: { label: "Key Projects", icon: Code },
  education: { label: "Education & Degrees", icon: GraduationCap },
  certificates: { label: "Certifications", icon: Certificate },
  awards: { label: "Honors & Awards", icon: Trophy },
  languages: { label: "Languages", icon: User },
};

export function CVVersionEditor({ versionId, onClose, onToast }: CVVersionEditorProps) {
  const { data: version, isLoading, isError, error } = useCvDetail(versionId);
  const updateMutation = useUpdateCvVersion();
  const exportPdfMutation = useExportPdf();
  const exportDocxMutation = useExportDocx();

  const [snapshot, setSnapshot] = useState<CVContentSnapshot | null>(null);
  const [initialJson, setInitialJson] = useState<string>("");
  const [showDiscardModal, setShowDiscardModal] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    basics: true,
    work: true,
    skills: true,
    projects: false,
    education: false,
    certificates: false,
    awards: false,
    languages: false,
  });

  // Export JSON Resume modal
  const [jsonResumeData, setJsonResumeData] = useState<Record<string, any> | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [activeMode, setActiveMode] = useState<"edit" | "preview">("edit");

  // Initialize draft snapshot from loaded version
  useEffect(() => {
    if (version?.content_snapshot && !snapshot) {
      const snap = version.content_snapshot;
      // Ensure presentation settings exist
      const pres: CVPresentationSnapshot = snap.presentation || {
        template: "modern",
        typography: "sans",
        color_scheme: "slate",
        section_order: snap.section_order || DEFAULT_SECTION_ORDER,
        section_visibility: {
          basics: true,
          work: true,
          skills: true,
          projects: true,
          education: true,
          certificates: true,
          awards: true,
          languages: true,
        },
        item_visibility: {},
      };

      const normalized: CVContentSnapshot = {
        ...snap,
        schema_version: snap.schema_version || "2.0.0",
        work: snap.work || snap.experiences || [],
        certificates: snap.certificates || snap.certifications || [],
        awards: snap.awards || snap.achievements || [],
        presentation: pres,
      };

      setSnapshot(normalized);
      setInitialJson(JSON.stringify(normalized));
    }
  }, [version, snapshot]);

  const isDirty = useMemo(() => {
    if (!snapshot || !initialJson) return false;
    return JSON.stringify(snapshot) !== initialJson;
  }, [snapshot, initialJson]);

  const handleCancelClick = () => {
    if (isDirty) {
      setShowDiscardModal(true);
    } else {
      onClose();
    }
  };

  const handleSave = async () => {
    if (!snapshot) return;
    try {
      await updateMutation.mutateAsync({
        id: versionId,
        payload: { content_snapshot: snapshot },
      });
      setInitialJson(JSON.stringify(snapshot));
      onToast("CV Version Saved", "Your version-specific customizations and presentation have been saved.", "success");
    } catch (err: any) {
      onToast("Save Failed", err?.message || "Failed to update CV version.", "error");
    }
  };

  const handleExportJsonResume = async () => {
    setIsExporting(true);
    try {
      const data = await cvApi.exportJsonResume(versionId, true);
      setJsonResumeData(data);
    } catch (err: any) {
      onToast("Export Failed", err?.message || "Could not export JSON Resume.", "error");
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportPdf = async () => {
    try {
      if (isDirty && snapshot) {
        await updateMutation.mutateAsync({
          id: versionId,
          payload: { content_snapshot: snapshot },
        });
        setInitialJson(JSON.stringify(snapshot));
      }
      await exportPdfMutation.mutateAsync({ id: versionId });
      onToast("PDF Exported", "Your CV PDF has been downloaded successfully.", "success");
    } catch (err: any) {
      onToast("PDF Export Failed", err?.message || "Failed to generate PDF.", "error");
    }
  };

  const handleExportDocx = async () => {
    try {
      if (isDirty && snapshot) {
        await updateMutation.mutateAsync({
          id: versionId,
          payload: { content_snapshot: snapshot },
        });
        setInitialJson(JSON.stringify(snapshot));
      }
      await exportDocxMutation.mutateAsync({ id: versionId });
      onToast("Word Document Exported", "Your editable DOCX CV has been downloaded successfully.", "success");
    } catch (err: any) {
      onToast("DOCX Export Failed", err?.message || "Failed to generate DOCX.", "error");
    }
  };

  const downloadJsonFile = () => {
    if (!jsonResumeData) return;
    const blob = new Blob([JSON.stringify(jsonResumeData, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${version?.name || "cv"}-resume.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Section Ordering
  const sectionOrder = useMemo(() => {
    const customOrder = snapshot?.presentation?.section_order || DEFAULT_SECTION_ORDER;
    const existing = new Set(customOrder);
    const full = [...customOrder];
    for (const s of DEFAULT_SECTION_ORDER) {
      if (!existing.has(s)) full.push(s);
    }
    return full;
  }, [snapshot]);

  const moveSection = (idx: number, direction: "up" | "down") => {
    if (!snapshot) return;
    const newOrder = [...sectionOrder];
    const targetIdx = direction === "up" ? idx - 1 : idx + 1;
    if (targetIdx < 0 || targetIdx >= newOrder.length) return;
    const temp = newOrder[idx];
    newOrder[idx] = newOrder[targetIdx];
    newOrder[targetIdx] = temp;

    setSnapshot({
      ...snapshot,
      presentation: {
        ...snapshot.presentation!,
        section_order: newOrder,
      },
    });
  };

  const toggleSectionVisibility = (secKey: string) => {
    if (!snapshot?.presentation) return;
    const current = snapshot.presentation.section_visibility?.[secKey] ?? true;
    setSnapshot({
      ...snapshot,
      presentation: {
        ...snapshot.presentation,
        section_visibility: {
          ...snapshot.presentation.section_visibility,
          [secKey]: !current,
        },
      },
    });
  };

  const toggleItemVisibility = (itemId: string) => {
    if (!snapshot?.presentation) return;
    const current = snapshot.presentation.item_visibility?.[itemId] ?? true;
    setSnapshot({
      ...snapshot,
      presentation: {
        ...snapshot.presentation,
        item_visibility: {
          ...snapshot.presentation.item_visibility,
          [itemId]: !current,
        },
      },
    });
  };

  const toggleSectionExpand = (secKey: string) => {
    setExpandedSections((prev) => ({ ...prev, [secKey]: !prev[secKey] }));
  };

  if (isLoading || !snapshot) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "var(--color-text-secondary)" }}>
        <p>Loading CV Version Editor…</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ padding: "2rem", background: "rgba(239,68,68,0.1)", borderRadius: "8px", margin: "2rem auto", maxWidth: "600px" }}>
        <h3 style={{ color: "var(--color-danger, #ef4444)", margin: "0 0 0.5rem" }}>Failed to Load Version</h3>
        <p style={{ margin: "0 0 1rem", fontSize: "0.85rem" }}>{error?.message || "Unknown error"}</p>
        <Button variant="secondary" onClick={onClose}>
          Back to Versions
        </Button>
      </div>
    );
  }

  const { basics, presentation } = snapshot;
  const itemVis = presentation?.item_visibility || {};
  const secVis = presentation?.section_visibility || {};

  return (
    <div className="workspace-container animate-fadeIn" style={{ maxWidth: "1000px", margin: "0 auto", paddingBottom: "5rem" }}>
      {/* Editor Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "1rem",
          padding: "1rem 0",
          borderBottom: "1px solid var(--color-border)",
          marginBottom: "1.5rem",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <IconButton label="Back to Versions" onClick={handleCancelClick}>
            <ArrowLeft size={18} weight="bold" />
          </IconButton>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h2 style={{ margin: 0, fontSize: "1.25rem", fontWeight: 700 }}>{version?.name}</h2>
              <Badge tone={version?.status === "ready" ? "success" : "blue"}>{version?.status.toUpperCase()}</Badge>
              {isDirty && <Badge tone="warning">Unsaved Changes</Badge>}
            </div>
            <p style={{ margin: "0.2rem 0 0", fontSize: "0.82rem", color: "var(--color-text-secondary)" }}>
              Customizing version-specific headline, bullet points, and section visibility. Master profile is untouched.
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", flexWrap: "wrap" }}>
          {/* View Mode Toggle */}
          <div style={{ display: "inline-flex", borderRadius: "6px", border: "1px solid var(--color-border)", padding: "2px", background: "var(--color-surface)" }}>
            <button
              type="button"
              onClick={() => setActiveMode("edit")}
              style={{
                padding: "0.3rem 0.65rem",
                borderRadius: "4px",
                border: "none",
                fontSize: "0.82rem",
                fontWeight: activeMode === "edit" ? 600 : 400,
                background: activeMode === "edit" ? "var(--color-primary-500)" : "transparent",
                color: activeMode === "edit" ? "#ffffff" : "var(--color-text-primary)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
              }}
            >
              Edit Content
            </button>
            <button
              type="button"
              onClick={() => setActiveMode("preview")}
              style={{
                padding: "0.3rem 0.65rem",
                borderRadius: "4px",
                border: "none",
                fontSize: "0.82rem",
                fontWeight: activeMode === "preview" ? 600 : 400,
                background: activeMode === "preview" ? "var(--color-primary-500)" : "transparent",
                color: activeMode === "preview" ? "#ffffff" : "var(--color-text-primary)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
              }}
            >
              <Eye size={15} />
              Preview & Templates
            </button>
          </div>

          <Button
            variant="secondary"
            size="sm"
            icon={<DownloadSimple size={16} />}
            loading={exportPdfMutation.isPending}
            disabled={exportPdfMutation.isPending || exportDocxMutation.isPending}
            onClick={handleExportPdf}
          >
            Export PDF
          </Button>

          <Button
            variant="secondary"
            size="sm"
            icon={<DownloadSimple size={16} />}
            loading={exportDocxMutation.isPending}
            disabled={exportPdfMutation.isPending || exportDocxMutation.isPending}
            onClick={handleExportDocx}
          >
            Export DOCX
          </Button>

          <Button
            variant="ghost"
            size="sm"
            icon={<DownloadSimple size={16} />}
            loading={isExporting}
            onClick={handleExportJsonResume}
          >
            JSON Resume
          </Button>
          <Button variant="ghost" size="sm" onClick={handleCancelClick}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={<FloppyDisk size={16} weight="bold" />}
            loading={updateMutation.isPending}
            disabled={!isDirty || updateMutation.isPending}
            onClick={handleSave}
          >
            Save Changes
          </Button>
        </div>
      </div>

      {activeMode === "preview" ? (
        <div style={{ marginTop: "0.5rem" }}>
          <CVRenderer
            snapshot={snapshot}
            onPresentationChange={(newPres) => {
              setSnapshot((prev) => (prev ? { ...prev, presentation: newPres } : null));
            }}
            onExportPdf={handleExportPdf}
            onExportDocx={handleExportDocx}
            isExportingPdf={exportPdfMutation.isPending}
            isExportingDocx={exportDocxMutation.isPending}
          />
        </div>
      ) : (
        /* Section List with Controls */
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {sectionOrder.map((secKey, idx) => {
          const meta = SECTION_METADATA[secKey] || { label: secKey, icon: User };
          const Icon = meta.icon;
          const isVisible = secVis[secKey] ?? true;
          const isExpanded = expandedSections[secKey] ?? false;

          return (
            <div
              key={secKey}
              style={{
                background: "var(--color-surface)",
                border: isVisible ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                opacity: isVisible ? 1 : 0.65,
                borderRadius: "10px",
                overflow: "hidden",
                transition: "all 0.15s ease",
              }}
            >
              {/* Section Header */}
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  padding: "0.85rem 1.25rem",
                  background: isVisible ? "var(--color-surface-hover)" : "transparent",
                  borderBottom: isExpanded ? "1px solid var(--color-border)" : "none",
                  cursor: "pointer",
                }}
                onClick={() => toggleSectionExpand(secKey)}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                  <Icon size={18} weight="bold" style={{ color: isVisible ? "var(--color-primary-500)" : "var(--color-text-tertiary)" }} />
                  <span style={{ fontWeight: 600, fontSize: "0.92rem", color: "var(--color-text-primary)" }}>
                    {meta.label}
                  </span>
                  {!isVisible && <Badge tone="neutral">Hidden in CV</Badge>}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }} onClick={(e) => e.stopPropagation()}>
                  {/* Reorder Buttons */}
                  <IconButton
                    label="Move Up"
                    disabled={idx === 0}
                    onClick={() => moveSection(idx, "up")}
                  >
                    <ArrowUp size={15} />
                  </IconButton>
                  <IconButton
                    label="Move Down"
                    disabled={idx === sectionOrder.length - 1}
                    onClick={() => moveSection(idx, "down")}
                  >
                    <ArrowDown size={15} />
                  </IconButton>

                  {/* Visibility Toggle Button */}
                  <IconButton
                    label={isVisible ? "Hide Section" : "Show Section"}
                    onClick={() => toggleSectionVisibility(secKey)}
                  >
                    {isVisible ? <Eye size={16} style={{ color: "var(--color-primary-500)" }} /> : <EyeSlash size={16} />}
                  </IconButton>
                </div>
              </div>

              {/* Section Content Editor (Accordion Body) */}
              {isExpanded && (
                <div style={{ padding: "1.25rem" }}>
                  {/* 1. Basics Editor */}
                  {secKey === "basics" && basics && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem" }}>
                        <Field
                          label="Full Name"
                          value={basics.name || ""}
                          onChange={(e) => {
                            const name = e.target.value;
                            setSnapshot({
                              ...snapshot,
                              basics: { ...basics, name },
                            });
                          }}
                        />
                        <Field
                          label="Professional Headline (Version-Specific)"
                          value={basics.label || basics.professional_headline || ""}
                          onChange={(e) => {
                            const label = e.target.value;
                            setSnapshot({
                              ...snapshot,
                              basics: {
                                ...basics,
                                label,
                                professional_headline: label,
                              },
                            });
                          }}
                        />
                      </div>

                      <TextareaField
                        label="Executive Summary (Version-Specific Pitch)"
                        rows={3}
                        value={basics.summary || basics.base_summary || ""}
                        onChange={(e) => {
                          const summary = e.target.value;
                          setSnapshot({
                            ...snapshot,
                            basics: {
                              ...basics,
                              summary,
                              base_summary: summary,
                            },
                          });
                        }}
                      />

                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem" }}>
                        <Field
                          label="Email"
                          value={basics.email || ""}
                          onChange={(e) =>
                            setSnapshot({
                              ...snapshot,
                              basics: { ...basics, email: e.target.value },
                            })
                          }
                        />
                        <Field
                          label="Phone"
                          value={basics.phone || ""}
                          onChange={(e) =>
                            setSnapshot({
                              ...snapshot,
                              basics: { ...basics, phone: e.target.value },
                            })
                          }
                        />
                        <Field
                          label="City"
                          value={basics.location?.city || basics.city || ""}
                          onChange={(e) => {
                            const city = e.target.value;
                            setSnapshot({
                              ...snapshot,
                              basics: {
                                ...basics,
                                city,
                                location: { ...(basics.location || {}), city },
                              },
                            });
                          }}
                        />
                        <Field
                          label="Country"
                          value={basics.location?.country || basics.country || ""}
                          onChange={(e) => {
                            const country = e.target.value;
                            setSnapshot({
                              ...snapshot,
                              basics: {
                                ...basics,
                                country,
                                location: { ...(basics.location || {}), country },
                              },
                            });
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* 2. Work Experiences Editor */}
                  {secKey === "work" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                      {(snapshot.work || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No work experiences recorded in snapshot.
                        </p>
                      ) : (
                        snapshot.work!.map((w, wIdx) => {
                          const wId = w.id ? String(w.id) : `work-${wIdx}`;
                          const isItemIncluded = itemVis[wId] !== false;

                          return (
                            <div
                              key={wId}
                              style={{
                                border: isItemIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                borderRadius: "8px",
                                padding: "1rem",
                                background: isItemIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                opacity: isItemIncluded ? 1 : 0.6,
                              }}
                            >
                              {/* Item Inclusion Bar */}
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`work-inc-${wId}`}
                                    checked={isItemIncluded}
                                    onChange={() => toggleItemVisibility(wId)}
                                    style={{ cursor: "pointer", width: "16px", height: "16px" }}
                                  />
                                  <label htmlFor={`work-inc-${wId}`} style={{ fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
                                    {w.position || "Position"} — {w.name || w.company || "Company"}
                                  </label>
                                </div>
                                <Badge tone={isItemIncluded ? "success" : "neutral"}>
                                  {isItemIncluded ? "Included in Version" : "Excluded"}
                                </Badge>
                              </div>

                              {/* Editable Fields */}
                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.6rem", marginBottom: "0.6rem" }}>
                                <Field
                                  label="Position Title"
                                  value={w.position || ""}
                                  disabled={!isItemIncluded}
                                  onChange={(e) => {
                                    const nextWork = [...snapshot.work!];
                                    nextWork[wIdx] = { ...w, position: e.target.value };
                                    setSnapshot({ ...snapshot, work: nextWork });
                                  }}
                                />
                                <Field
                                  label="Company / Organization"
                                  value={w.name || w.company || ""}
                                  disabled={!isItemIncluded}
                                  onChange={(e) => {
                                    const nextWork = [...snapshot.work!];
                                    nextWork[wIdx] = { ...w, name: e.target.value, company: e.target.value };
                                    setSnapshot({ ...snapshot, work: nextWork });
                                  }}
                                />
                                <Field
                                  label="Location"
                                  value={w.location || ""}
                                  disabled={!isItemIncluded}
                                  onChange={(e) => {
                                    const nextWork = [...snapshot.work!];
                                    nextWork[wIdx] = { ...w, location: e.target.value };
                                    setSnapshot({ ...snapshot, work: nextWork });
                                  }}
                                />
                              </div>

                              <TextareaField
                                label="Role Summary"
                                rows={2}
                                value={w.summary || w.description || ""}
                                disabled={!isItemIncluded}
                                onChange={(e) => {
                                  const nextWork = [...snapshot.work!];
                                  nextWork[wIdx] = { ...w, summary: e.target.value, description: e.target.value };
                                  setSnapshot({ ...snapshot, work: nextWork });
                                }}
                              />

                              {/* Highlights / Bullet Points Manager */}
                              <div style={{ marginTop: "0.75rem" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                                  <span style={{ fontSize: "0.8rem", fontWeight: 600, color: "var(--color-text-secondary)" }}>
                                    Key Accomplishments & Bullet Points ({w.highlights?.length || 0})
                                  </span>
                                  {isItemIncluded && (
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      icon={<Plus size={14} />}
                                      onClick={() => {
                                        const nextWork = [...snapshot.work!];
                                        const currentHighlights = listHighlights(w);
                                        nextWork[wIdx] = { ...w, highlights: [...currentHighlights, ""] };
                                        setSnapshot({ ...snapshot, work: nextWork });
                                      }}
                                    >
                                      Add Bullet
                                    </Button>
                                  )}
                                </div>

                                <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
                                  {listHighlights(w).map((bullet, bIdx) => (
                                    <div key={bIdx} style={{ display: "flex", gap: "0.4rem", alignItems: "center" }}>
                                      <input
                                        type="text"
                                        aria-label={`Bullet point ${bIdx + 1}`}
                                        value={bullet}
                                        disabled={!isItemIncluded}
                                        onChange={(e) => {
                                          const nextWork = [...snapshot.work!];
                                          const currentHighlights = [...listHighlights(w)];
                                          currentHighlights[bIdx] = e.target.value;
                                          nextWork[wIdx] = { ...w, highlights: currentHighlights };
                                          setSnapshot({ ...snapshot, work: nextWork });
                                        }}
                                        style={{
                                          flex: 1,
                                          fontSize: "0.82rem",
                                          padding: "0.4rem 0.6rem",
                                          borderRadius: "6px",
                                          border: "1px solid var(--color-border)",
                                          background: "var(--color-surface)",
                                        }}
                                      />
                                      {isItemIncluded && (
                                        <IconButton
                                          label="Delete bullet"
                                          onClick={() => {
                                            const nextWork = [...snapshot.work!];
                                            const currentHighlights = listHighlights(w).filter((_, idx) => idx !== bIdx);
                                            nextWork[wIdx] = { ...w, highlights: currentHighlights };
                                            setSnapshot({ ...snapshot, work: nextWork });
                                          }}
                                        >
                                          <Trash size={14} style={{ color: "var(--color-danger, #ef4444)" }} />
                                        </IconButton>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  )}

                  {/* 3. Skills Editor */}
                  {secKey === "skills" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.skills || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No skills recorded in snapshot.
                        </p>
                      ) : (
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "0.75rem" }}>
                          {snapshot.skills!.map((s, sIdx) => {
                            const sId = s.id ? String(s.id) : `skill-${sIdx}`;
                            const isIncluded = itemVis[sId] !== false;

                            return (
                              <div
                                key={sId}
                                style={{
                                  border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                  borderRadius: "6px",
                                  padding: "0.75rem",
                                  background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                  gap: "0.5rem",
                                  opacity: isIncluded ? 1 : 0.6,
                                }}
                              >
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flex: 1 }}>
                                  <input
                                    type="checkbox"
                                    id={`skill-inc-${sId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(sId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <input
                                    type="text"
                                    value={s.name}
                                    disabled={!isIncluded}
                                    onChange={(e) => {
                                      const next = [...snapshot.skills!];
                                      next[sIdx] = { ...s, name: e.target.value };
                                      setSnapshot({ ...snapshot, skills: next });
                                    }}
                                    style={{
                                      fontSize: "0.85rem",
                                      fontWeight: 600,
                                      border: "none",
                                      background: "transparent",
                                      width: "100%",
                                      color: "var(--color-text-primary)",
                                    }}
                                  />
                                </div>
                                <span style={{ fontSize: "0.75rem", color: "var(--color-text-tertiary)" }}>
                                  {s.level || s.proficiency || ""}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}

                  {/* 4. Projects Editor */}
                  {secKey === "projects" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.projects || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No projects recorded in snapshot.
                        </p>
                      ) : (
                        snapshot.projects!.map((p, pIdx) => {
                          const pId = p.id ? String(p.id) : `project-${pIdx}`;
                          const isIncluded = itemVis[pId] !== false;

                          return (
                            <div
                              key={pId}
                              style={{
                                border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                borderRadius: "8px",
                                padding: "0.85rem",
                                background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                opacity: isIncluded ? 1 : 0.6,
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`proj-inc-${pId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(pId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <label htmlFor={`proj-inc-${pId}`} style={{ fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
                                    {p.name}
                                  </label>
                                </div>
                                <Badge tone={isIncluded ? "success" : "neutral"}>
                                  {isIncluded ? "Included" : "Excluded"}
                                </Badge>
                              </div>

                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem", marginBottom: "0.5rem" }}>
                                <Field
                                  label="Project Name"
                                  value={p.name}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.projects!];
                                    next[pIdx] = { ...p, name: e.target.value };
                                    setSnapshot({ ...snapshot, projects: next });
                                  }}
                                />
                                <Field
                                  label="Live / Demo URL"
                                  value={p.url || p.live_url || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.projects!];
                                    next[pIdx] = { ...p, url: e.target.value, live_url: e.target.value };
                                    setSnapshot({ ...snapshot, projects: next });
                                  }}
                                />
                              </div>

                              <TextareaField
                                label="Project Description"
                                rows={2}
                                value={p.description || ""}
                                disabled={!isIncluded}
                                onChange={(e) => {
                                  const next = [...snapshot.projects!];
                                  next[pIdx] = { ...p, description: e.target.value };
                                  setSnapshot({ ...snapshot, projects: next });
                                }}
                              />
                            </div>
                          );
                        })
                      )}
                    </div>
                  )}

                  {/* 5. Education Editor */}
                  {secKey === "education" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.education || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No education records in snapshot.
                        </p>
                      ) : (
                        snapshot.education!.map((edu, eduIdx) => {
                          const eduId = edu.id ? String(edu.id) : `edu-${eduIdx}`;
                          const isIncluded = itemVis[eduId] !== false;

                          return (
                            <div
                              key={eduId}
                              style={{
                                border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                borderRadius: "8px",
                                padding: "0.85rem",
                                background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                opacity: isIncluded ? 1 : 0.6,
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`edu-inc-${eduId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(eduId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <label htmlFor={`edu-inc-${eduId}`} style={{ fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
                                    {edu.studyType || edu.degree || "Degree"} — {edu.institution}
                                  </label>
                                </div>
                                <Badge tone={isIncluded ? "success" : "neutral"}>
                                  {isIncluded ? "Included" : "Excluded"}
                                </Badge>
                              </div>

                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem" }}>
                                <Field
                                  label="Degree / Study Type"
                                  value={edu.studyType || edu.degree || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.education!];
                                    next[eduIdx] = { ...edu, studyType: e.target.value, degree: e.target.value };
                                    setSnapshot({ ...snapshot, education: next });
                                  }}
                                />
                                <Field
                                  label="Institution"
                                  value={edu.institution || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.education!];
                                    next[eduIdx] = { ...edu, institution: e.target.value };
                                    setSnapshot({ ...snapshot, education: next });
                                  }}
                                />
                                <Field
                                  label="Field of Study / Area"
                                  value={edu.area || edu.field_of_study || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.education!];
                                    next[eduIdx] = { ...edu, area: e.target.value, field_of_study: e.target.value };
                                    setSnapshot({ ...snapshot, education: next });
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  )}

                  {/* 6. Certificates Editor */}
                  {secKey === "certificates" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.certificates || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No certificates in snapshot.
                        </p>
                      ) : (
                        snapshot.certificates!.map((cert, cIdx) => {
                          const cId = cert.id ? String(cert.id) : `cert-${cIdx}`;
                          const isIncluded = itemVis[cId] !== false;

                          return (
                            <div
                              key={cId}
                              style={{
                                border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                borderRadius: "8px",
                                padding: "0.85rem",
                                background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                opacity: isIncluded ? 1 : 0.6,
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`cert-inc-${cId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(cId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <label htmlFor={`cert-inc-${cId}`} style={{ fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
                                    {cert.name} — {cert.issuer || "Issuer"}
                                  </label>
                                </div>
                                <Badge tone={isIncluded ? "success" : "neutral"}>
                                  {isIncluded ? "Included" : "Excluded"}
                                </Badge>
                              </div>

                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem" }}>
                                <Field
                                  label="Certificate Name"
                                  value={cert.name}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.certificates!];
                                    next[cIdx] = { ...cert, name: e.target.value };
                                    setSnapshot({ ...snapshot, certificates: next });
                                  }}
                                />
                                <Field
                                  label="Issuing Organization"
                                  value={cert.issuer || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.certificates!];
                                    next[cIdx] = { ...cert, issuer: e.target.value };
                                    setSnapshot({ ...snapshot, certificates: next });
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  )}

                  {/* 7. Awards Editor */}
                  {secKey === "awards" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.awards || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No honors or awards in snapshot.
                        </p>
                      ) : (
                        snapshot.awards!.map((a, aIdx) => {
                          const aId = a.id ? String(a.id) : `award-${aIdx}`;
                          const isIncluded = itemVis[aId] !== false;

                          return (
                            <div
                              key={aId}
                              style={{
                                border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                borderRadius: "8px",
                                padding: "0.85rem",
                                background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                opacity: isIncluded ? 1 : 0.6,
                              }}
                            >
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`award-inc-${aId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(aId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <label htmlFor={`award-inc-${aId}`} style={{ fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
                                    {a.title}
                                  </label>
                                </div>
                                <Badge tone={isIncluded ? "success" : "neutral"}>
                                  {isIncluded ? "Included" : "Excluded"}
                                </Badge>
                              </div>

                              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.5rem" }}>
                                <Field
                                  label="Award Title"
                                  value={a.title}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.awards!];
                                    next[aIdx] = { ...a, title: e.target.value };
                                    setSnapshot({ ...snapshot, awards: next });
                                  }}
                                />
                                <Field
                                  label="Awarder / Issuer"
                                  value={a.awarder || a.issuer || ""}
                                  disabled={!isIncluded}
                                  onChange={(e) => {
                                    const next = [...snapshot.awards!];
                                    next[aIdx] = { ...a, awarder: e.target.value, issuer: e.target.value };
                                    setSnapshot({ ...snapshot, awards: next });
                                  }}
                                />
                              </div>
                            </div>
                          );
                        })
                      )}
                    </div>
                  )}

                  {/* 8. Languages Editor */}
                  {secKey === "languages" && (
                    <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                      {(snapshot.languages || []).length === 0 ? (
                        <p style={{ fontSize: "0.85rem", color: "var(--color-text-tertiary)", margin: 0 }}>
                          No languages in snapshot.
                        </p>
                      ) : (
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "0.5rem" }}>
                          {snapshot.languages!.map((l, lIdx) => {
                            const lId = l.id ? String(l.id) : `lang-${lIdx}`;
                            const isIncluded = itemVis[lId] !== false;

                            return (
                              <div
                                key={lId}
                                style={{
                                  border: isIncluded ? "1px solid var(--color-border)" : "1px dashed var(--color-border)",
                                  borderRadius: "6px",
                                  padding: "0.75rem",
                                  background: isIncluded ? "var(--color-surface)" : "var(--color-surface-hover)",
                                  display: "flex",
                                  justifyContent: "space-between",
                                  alignItems: "center",
                                  opacity: isIncluded ? 1 : 0.6,
                                }}
                              >
                                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                  <input
                                    type="checkbox"
                                    id={`lang-inc-${lId}`}
                                    checked={isIncluded}
                                    onChange={() => toggleItemVisibility(lId)}
                                    style={{ cursor: "pointer" }}
                                  />
                                  <span style={{ fontWeight: 600, fontSize: "0.85rem" }}>
                                    {l.language || l.name}
                                  </span>
                                </div>
                                <span style={{ fontSize: "0.78rem", color: "var(--color-text-tertiary)" }}>
                                  {l.fluency || l.proficiency || ""}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      )}

      {/* Discard Unsaved Changes Confirmation Dialog */}
      <Modal
        open={showDiscardModal}
        onClose={() => setShowDiscardModal(false)}
        title="Discard Unsaved Changes?"
        description="You have unsaved changes to this CV version. Are you sure you want to discard them?"
      >
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "1rem" }}>
          <Button variant="ghost" onClick={() => setShowDiscardModal(false)}>
            Keep Editing
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              setShowDiscardModal(false);
              onClose();
            }}
          >
            Discard Changes
          </Button>
        </div>
      </Modal>

      {/* JSON Resume Modal Preview */}
      <Modal
        open={Boolean(jsonResumeData)}
        onClose={() => setJsonResumeData(null)}
        title="Standard JSON Resume Output"
        description="Clean, standard JSON Resume export with application-specific extensions stripped according to Phase 2.3 specifications."
      >
        <div style={{ maxHeight: "60vh", overflowY: "auto", background: "var(--color-surface-hover)", borderRadius: "8px", padding: "1rem", marginBottom: "1rem" }}>
          <pre style={{ margin: 0, fontSize: "0.78rem", fontFamily: "monospace", whiteSpace: "pre-wrap", color: "var(--color-text-primary)" }}>
            {JSON.stringify(jsonResumeData, null, 2)}
          </pre>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
          <Button variant="secondary" onClick={() => setJsonResumeData(null)}>
            Close
          </Button>
          <Button variant="primary" icon={<DownloadSimple size={16} />} onClick={downloadJsonFile}>
            Download .json
          </Button>
        </div>
      </Modal>
    </div>
  );
}

function listHighlights(w: CVWorkSnapshot): string[] {
  if (w.highlights && w.highlights.length > 0) return w.highlights;
  const resps = w.responsibilities || [];
  const achs = w.achievements || [];
  return [...resps, ...achs];
}
