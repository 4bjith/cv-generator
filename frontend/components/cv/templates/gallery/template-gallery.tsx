"use client";

import React from "react";
import { Check, Sparkle } from "@phosphor-icons/react";
import { Badge } from "@/components/ui";
import { getAllTemplates, getTemplate } from "../registry";
import { TemplateDefinition, TemplateId } from "../types";

export interface TemplateGalleryProps {
  selectedTemplateId: TemplateId;
  onSelectTemplate: (templateId: TemplateId) => void;
  className?: string;
  style?: React.CSSProperties;
}

// ----------------------------------------------------------------------
// Accurate Miniature Previews for each Template
// ----------------------------------------------------------------------
function TemplateMiniaturePreview({ templateId }: { templateId: TemplateId }) {
  const t = getTemplate(templateId);

  switch (t.id) {
    case "modern-professional":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "6px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ height: "6px", width: "45px", background: "#0f172a", borderRadius: "2px" }} />
              <div style={{ height: "4px", width: "30px", background: "#2563eb", borderRadius: "2px", marginTop: "3px" }} />
            </div>
            <div style={{ width: "16px", height: "16px", borderRadius: "50%", background: "#e2e8f0" }} />
          </div>
          {/* Contact Bar */}
          <div style={{ height: "2px", width: "100%", background: "#f1f5f9" }} />
          {/* Summary */}
          <div style={{ height: "3px", width: "100%", background: "#e2e8f0", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "85%", background: "#e2e8f0", borderRadius: "1px" }} />
          {/* Section 1 */}
          <div style={{ borderBottom: "1.5px solid #2563eb", paddingBottom: "2px", marginTop: "4px" }}>
            <div style={{ height: "4px", width: "35px", background: "#0f172a", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "90%", background: "#94a3b8", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "75%", background: "#cbd5e1", borderRadius: "1px" }} />
          {/* Section 2 */}
          <div style={{ borderBottom: "1.5px solid #2563eb", paddingBottom: "2px", marginTop: "2px" }}>
            <div style={{ height: "4px", width: "30px", background: "#0f172a", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "80%", background: "#94a3b8", borderRadius: "1px" }} />
        </div>
      );

    case "classic-executive":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "5px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Centered Executive Header with Double Rule */}
          <div style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", borderBottom: "2px double #1e293b", paddingBottom: "4px" }}>
            <div style={{ height: "6px", width: "55px", background: "#1e293b", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "35px", background: "#64748b", borderRadius: "1px", marginTop: "2px" }} />
            <div style={{ height: "2px", width: "70%", background: "#cbd5e1", marginTop: "3px" }} />
          </div>
          {/* Section 1 */}
          <div style={{ borderBottom: "1px solid #1e293b", paddingBottom: "2px", marginTop: "3px" }}>
            <div style={{ height: "4px", width: "40px", background: "#1e293b", borderRadius: "1px" }} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <div style={{ height: "4px", width: "45px", background: "#334155", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "20px", background: "#94a3b8", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "90%", background: "#cbd5e1", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "80%", background: "#cbd5e1", borderRadius: "1px" }} />
          {/* Section 2 */}
          <div style={{ borderBottom: "1px solid #1e293b", paddingBottom: "2px", marginTop: "2px" }}>
            <div style={{ height: "4px", width: "35px", background: "#1e293b", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "85%", background: "#cbd5e1", borderRadius: "1px" }} />
        </div>
      );

    case "ats-minimal":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #000000",
            borderRadius: "6px",
            padding: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "5px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Strict Linear Header */}
          <div style={{ height: "7px", width: "50px", background: "#000000", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "70px", background: "#555555", borderRadius: "1px" }} />
          <div style={{ height: "2px", width: "100%", background: "#000000", margin: "2px 0" }} />
          {/* Standard Linear Sections */}
          <div style={{ height: "4px", width: "35px", background: "#000000", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "95%", background: "#666666", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "88%", background: "#666666", borderRadius: "1px" }} />
          <div style={{ height: "2px", width: "100%", background: "#000000", margin: "2px 0" }} />
          <div style={{ height: "4px", width: "40px", background: "#000000", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "90%", background: "#666666", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "80%", background: "#666666", borderRadius: "1px" }} />
        </div>
      );

    case "technical-developer":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "5px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Terminal Accent Line */}
          <div style={{ borderLeft: "3px solid #0284c7", paddingLeft: "4px" }}>
            <div style={{ height: "6px", width: "45px", background: "#0f172a", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "30px", background: "#0284c7", borderRadius: "1px", marginTop: "2px" }} />
          </div>
          {/* Tech Skills Pills */}
          <div style={{ display: "flex", gap: "3px", marginTop: "3px" }}>
            <div style={{ height: "7px", width: "16px", background: "#e0f2fe", borderRadius: "2px" }} />
            <div style={{ height: "7px", width: "18px", background: "#e0f2fe", borderRadius: "2px" }} />
            <div style={{ height: "7px", width: "14px", background: "#e0f2fe", borderRadius: "2px" }} />
          </div>
          {/* Section 1 */}
          <div style={{ borderBottom: "1px dashed #0284c7", paddingBottom: "2px", marginTop: "3px" }}>
            <div style={{ height: "4px", width: "35px", background: "#0284c7", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "90%", background: "#475569", borderRadius: "1px" }} />
          <div style={{ display: "flex", gap: "3px", marginTop: "2px" }}>
            <div style={{ height: "5px", width: "24px", background: "#f1f5f9", borderRadius: "2px" }} />
            <div style={{ height: "5px", width: "20px", background: "#f1f5f9", borderRadius: "2px" }} />
          </div>
        </div>
      );

    case "contemporary-two-column":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "8px",
            display: "grid",
            gridTemplateColumns: "30% 70%",
            gap: "6px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Sidebar */}
          <div style={{ background: "#f8fafc", padding: "4px", borderRadius: "4px", display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ width: "14px", height: "14px", borderRadius: "3px", background: "#e0e7ff" }} />
            <div style={{ height: "3px", width: "100%", background: "#4f46e5", borderRadius: "1px" }} />
            <div style={{ height: "2px", width: "80%", background: "#cbd5e1" }} />
            <div style={{ height: "2px", width: "70%", background: "#cbd5e1" }} />
            <div style={{ height: "3px", width: "100%", background: "#4f46e5", borderRadius: "1px", marginTop: "3px" }} />
            <div style={{ height: "2px", width: "90%", background: "#cbd5e1" }} />
            <div style={{ height: "2px", width: "85%", background: "#cbd5e1" }} />
          </div>
          {/* Main Column */}
          <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
            <div style={{ height: "6px", width: "50px", background: "#0f172a", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "35px", background: "#4f46e5", borderRadius: "1px" }} />
            <div style={{ height: "1px", width: "100%", background: "#e2e8f0", margin: "2px 0" }} />
            <div style={{ height: "4px", width: "30px", background: "#0f172a", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "95%", background: "#64748b", borderRadius: "1px" }} />
            <div style={{ height: "3px", width: "85%", background: "#64748b", borderRadius: "1px" }} />
            <div style={{ height: "4px", width: "25px", background: "#0f172a", borderRadius: "1px", marginTop: "3px" }} />
            <div style={{ height: "3px", width: "90%", background: "#64748b", borderRadius: "1px" }} />
          </div>
        </div>
      );

    case "academic-research":
      return (
        <div
          aria-hidden="true"
          style={{
            width: "100%",
            height: "140px",
            background: "#ffffff",
            border: "1px solid #e2e8f0",
            borderRadius: "6px",
            padding: "8px",
            display: "flex",
            flexDirection: "column",
            gap: "4px",
            overflow: "hidden",
            boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
          }}
        >
          {/* Formal Scholarly Header */}
          <div style={{ textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", borderBottom: "1px solid #78716c", paddingBottom: "3px" }}>
            <div style={{ height: "5px", width: "60px", background: "#1c1917", borderRadius: "1px" }} />
            <div style={{ height: "2px", width: "70%", background: "#78716c", marginTop: "2px" }} />
          </div>
          {/* Education first */}
          <div style={{ borderBottom: "1px solid #1c1917", paddingBottom: "1px", marginTop: "2px" }}>
            <div style={{ height: "3px", width: "45px", background: "#1c1917", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "90%", background: "#57534e", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "80%", background: "#78716c", borderRadius: "1px" }} />
          {/* Publications & Research */}
          <div style={{ borderBottom: "1px solid #1c1917", paddingBottom: "1px", marginTop: "2px" }}>
            <div style={{ height: "3px", width: "50px", background: "#1c1917", borderRadius: "1px" }} />
          </div>
          <div style={{ height: "3px", width: "95%", background: "#57534e", borderRadius: "1px" }} />
          <div style={{ height: "3px", width: "85%", background: "#78716c", borderRadius: "1px" }} />
        </div>
      );

    default:
      return null;
  }
}

// ----------------------------------------------------------------------
// Responsive Gallery Grid Component
// ----------------------------------------------------------------------
export function TemplateGallery({
  selectedTemplateId,
  onSelectTemplate,
  className = "",
  style,
}: TemplateGalleryProps) {
  const templates = getAllTemplates();
  const current = getTemplate(selectedTemplateId);

  return (
    <div className={`template-gallery-container ${className}`} style={style}>
      {/* Gallery Header Info */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, color: "var(--color-text-primary, #0f172a)" }}>
            Choose CV Template
          </h3>
          <p style={{ margin: "0.2rem 0 0", fontSize: "0.82rem", color: "var(--color-text-secondary, #64748b)" }}>
            Switch between 6 production-grade, print-ready layouts tailored for different career stages and industries.
          </p>
        </div>
        <Badge tone="blue">Active: {current.name}</Badge>
      </div>

      {/* Grid of 6 Distinct Templates */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "1.25rem",
        }}
      >
        {templates.map((tpl) => {
          const isSelected = tpl.id === current.id;

          return (
            <div
              key={tpl.id}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              onClick={() => onSelectTemplate(tpl.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onSelectTemplate(tpl.id);
                }
              }}
              style={{
                background: "#ffffff",
                border: isSelected ? "2px solid var(--color-primary-500, #2563eb)" : "1px solid var(--color-border, #e2e8f0)",
                borderRadius: "10px",
                padding: "1rem",
                display: "flex",
                flexDirection: "column",
                gap: "0.75rem",
                cursor: "pointer",
                position: "relative",
                transition: "all 0.18s ease",
                boxShadow: isSelected ? "0 4px 12px rgba(37, 99, 235, 0.15)" : "0 1px 3px rgba(0,0,0,0.05)",
                outline: "none",
              }}
            >
              {/* Selected Badge */}
              {isSelected && (
                <div
                  style={{
                    position: "absolute",
                    top: "10px",
                    right: "10px",
                    background: "var(--color-primary-500, #2563eb)",
                    color: "#ffffff",
                    borderRadius: "50%",
                    width: "22px",
                    height: "22px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                  }}
                >
                  <Check size={14} weight="bold" />
                </div>
              )}

              {/* Miniature Preview */}
              <TemplateMiniaturePreview templateId={tpl.id} />

              {/* Template Metadata */}
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginBottom: "0.25rem" }}>
                  <h4 style={{ margin: 0, fontSize: "0.95rem", fontWeight: 700, color: "var(--color-text-primary, #0f172a)" }}>
                    {tpl.name}
                  </h4>
                  <Badge tone={tpl.category === "ATS" ? "success" : tpl.category === "Executive" ? "amber" : "neutral"}>
                    {tpl.category}
                  </Badge>
                </div>
                <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--color-text-secondary, #64748b)", lineHeight: 1.4 }}>
                  {tpl.description}
                </p>
              </div>

              {/* Recommended For */}
              <div style={{ marginTop: "auto", paddingTop: "0.5rem", borderTop: "1px solid var(--color-border, #e2e8f0)", fontSize: "0.75rem", color: "var(--color-text-tertiary, #94a3b8)" }}>
                <strong style={{ color: "var(--color-text-secondary, #64748b)" }}>Best for: </strong>
                {tpl.recommendedFor}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
