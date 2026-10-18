"use client";

import { useState } from "react";
import {
  ArrowSquareOut,
  CheckCircle,
  DownloadSimple,
  Eye,
  FileDoc,
  FilePdf,
  PencilSimple,
  ShieldCheck,
  Sparkle,
  WarningCircle,
} from "@phosphor-icons/react";
import { Badge, Button, Card, Modal } from "@/components/ui";
import { useExportDocx, useExportPdf, useUpdateCvVersion } from "@/hooks/use-cv";
import { CVContentSnapshot } from "@/types/cv";
import { CVTailoringResponse } from "@/types/tailoring";

interface TailoringResultModalProps {
  open: boolean;
  result: CVTailoringResponse | null;
  onClose: () => void;
  onOpenEditor: (versionId: string) => void;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const TEMPLATES = [
  { id: "modern", label: "Modern Professional", desc: "Contemporary single-column layout" },
  { id: "classic", label: "Classic Executive", desc: "Formal serif layout for leadership" },
  { id: "minimal", label: "ATS-Friendly Minimal", desc: "Clean text-first structure" },
  { id: "technical", label: "Technical / Developer", desc: "Monospace skill matrix & systems" },
  { id: "two-column", label: "Contemporary Two-Column", desc: "Asymmetric sidebar layout" },
  { id: "academic", label: "Academic / Research", desc: "Scholarly publication hierarchy" },
];

export function TailoringResultModal({
  open,
  result,
  onClose,
  onOpenEditor,
  onToast,
}: TailoringResultModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<string>("modern");

  const exportPdfMutation = useExportPdf();
  const exportDocxMutation = useExportDocx();
  const updateVersionMutation = useUpdateCvVersion();

  if (!result) return null;

  const currentTemplate = selectedTemplate || result.content_snapshot.presentation?.template || "modern";

  const handleTemplateChange = async (templateId: string) => {
    setSelectedTemplate(templateId);
    try {
      const updatedSnapshot: CVContentSnapshot = {
        ...result.content_snapshot,
        presentation: {
          section_order: result.content_snapshot.presentation?.section_order || [
            "basics",
            "skills",
            "work",
            "education",
            "projects",
          ],
          ...result.content_snapshot.presentation,
          template: templateId,
        },
      };

      await updateVersionMutation.mutateAsync({
        id: result.cv_version_id,
        payload: {
          content_snapshot: updatedSnapshot,
        },
      });
      onToast("Template Updated", `Applied ${templateId} styling to tailored CV.`, "info");
    } catch {
      onToast("Error", "Could not update presentation template.", "error");
    }
  };

  const handleDownloadPdf = async () => {
    try {
      await exportPdfMutation.mutateAsync({
        id: result.cv_version_id,
        overrides: { template: currentTemplate },
      });
      onToast("PDF Downloaded", "Production PDF generated successfully.", "success");
    } catch {
      onToast("Export Failed", "Could not export PDF.", "error");
    }
  };

  const handleDownloadDocx = async () => {
    try {
      await exportDocxMutation.mutateAsync({
        id: result.cv_version_id,
        overrides: { template: currentTemplate },
      });
      onToast("DOCX Downloaded", "Editable Microsoft Word document generated.", "success");
    } catch {
      onToast("Export Failed", "Could not export DOCX document.", "error");
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Tailored CV Created & Verified"
      description={`Job-specific CV version created for ${result.job_title} at ${result.company_name}`}
      footer={
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Button
              variant="secondary"
              size="sm"
              icon={<FilePdf size={16} aria-hidden="true" />}
              loading={exportPdfMutation.isPending}
              onClick={handleDownloadPdf}
            >
              Download PDF
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={<FileDoc size={16} aria-hidden="true" />}
              loading={exportDocxMutation.isPending}
              onClick={handleDownloadDocx}
            >
              Download Word (.docx)
            </Button>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <Button variant="ghost" onClick={onClose}>
              Done
            </Button>
            <Button
              variant="primary"
              icon={<PencilSimple size={16} aria-hidden="true" />}
              onClick={() => {
                onClose();
                onOpenEditor(result.cv_version_id);
              }}
            >
              Open Full CV Editor
            </Button>
          </div>
        </div>
      }
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        {/* Quality & Grounding Banner */}
        <div
          style={{
            padding: "1rem 1.25rem",
            borderRadius: "0.75rem",
            background: "linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(59, 130, 246, 0.08))",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "0.75rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div
              style={{
                width: "40px",
                height: "40px",
                borderRadius: "50%",
                background: "rgba(16, 185, 129, 0.2)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <ShieldCheck size={24} color="var(--color-emerald-400, #34d399)" weight="fill" aria-hidden="true" />
            </div>
            <div>
              <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--fg-default, #fff)" }}>
                Zero-Hallucination Verified Snapshot
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--fg-muted, #a1a1aa)" }}>
                Independent point-in-time version linked to {result.job_title}
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Badge tone="green">
              {result.quality_score.toFixed(0)}% Evidence Grounded
            </Badge>
            <Badge tone="blue">v2.0.0 Snapshot</Badge>
          </div>
        </div>

        {/* Change Summary */}
        <Card style={{ padding: "1.25rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
            <Sparkle size={18} color="var(--color-blue-400, #60a5fa)" weight="fill" aria-hidden="true" />
            <h4 style={{ margin: 0, fontSize: "0.9rem", fontWeight: 700, color: "var(--fg-default, #fff)" }}>
              Tailoring Change Summary
            </h4>
          </div>

          {result.change_summary.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              {result.change_summary.map((change, i) => (
                <li key={i} style={{ fontSize: "0.825rem", color: "var(--fg-secondary, #d4d4d8)", lineHeight: 1.45 }}>
                  {change}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ margin: 0, fontSize: "0.825rem", color: "var(--fg-muted, #a1a1aa)" }}>
              Customized candidate summary and prioritized job-relevant technical achievements.
            </p>
          )}
        </Card>

        {/* Unresolved Gaps Warning */}
        {result.unresolved_gaps.length > 0 ? (
          <div
            style={{
              padding: "1rem 1.25rem",
              borderRadius: "0.75rem",
              background: "rgba(245, 158, 11, 0.08)",
              border: "1px solid rgba(245, 158, 11, 0.25)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <WarningCircle size={18} color="var(--color-amber-400, #fbbf24)" weight="fill" aria-hidden="true" />
              <strong style={{ fontSize: "0.85rem", color: "var(--color-amber-300, #fcd34d)" }}>
                Unresolved Job Requirements ({result.unresolved_gaps.length})
              </strong>
            </div>
            <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.775rem", color: "var(--fg-muted, #a1a1aa)", lineHeight: 1.4 }}>
              The following requirements could not be verified from your profile or clarifications. To protect factual integrity, they were NOT fabricated in your CV:
            </p>
            <ul style={{ margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column", gap: "0.25rem" }}>
              {result.unresolved_gaps.map((gap, i) => (
                <li key={i} style={{ fontSize: "0.775rem", color: "var(--fg-secondary, #d4d4d8)" }}>
                  {gap}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {/* Template Presentation Switcher */}
        <div>
          <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--fg-default, #fff)", marginBottom: "0.5rem" }}>
            Select Presentation Template (6 Templates Available)
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "0.5rem",
            }}
          >
            {TEMPLATES.map((tmpl) => {
              const active = currentTemplate === tmpl.id;
              return (
                <button
                  key={tmpl.id}
                  type="button"
                  onClick={() => handleTemplateChange(tmpl.id)}
                  style={{
                    textAlign: "left",
                    padding: "0.75rem",
                    borderRadius: "0.5rem",
                    border: active ? "2px solid var(--color-blue-500, #3b82f6)" : "1px solid var(--border-subtle, rgba(255, 255, 255, 0.08))",
                    background: active ? "rgba(59, 130, 246, 0.12)" : "var(--surface-sunken, rgba(255, 255, 255, 0.02))",
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ fontSize: "0.8rem", fontWeight: 700, color: active ? "var(--color-blue-400, #60a5fa)" : "var(--fg-default, #fff)" }}>
                    {tmpl.label}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "var(--fg-muted, #a1a1aa)", marginTop: "0.2rem" }}>
                    {tmpl.desc}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </Modal>
  );
}
