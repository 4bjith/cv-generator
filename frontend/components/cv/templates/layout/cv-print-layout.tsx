"use client";

import React, { ReactNode, useState } from "react";
import { DownloadSimple, MagnifyingGlassMinus, MagnifyingGlassPlus, Printer } from "@phosphor-icons/react";
import { Button } from "@/components/ui";
import { ColorScheme, PageSize, SpacingScale, TypographyStyle } from "../types";

export interface CVPrintLayoutProps {
  children: ReactNode;
  pageSize?: PageSize;
  typography?: TypographyStyle | string;
  colorScheme?: ColorScheme | string;
  spacing?: SpacingScale | string;
  showToolbar?: boolean;
  onPageSizeChange?: (size: PageSize) => void;
  onSpacingChange?: (spacing: SpacingScale) => void;
  onPrint?: () => void;
  onExportPdf?: () => void;
  onExportDocx?: () => void;
  isExportingPdf?: boolean;
  isExportingDocx?: boolean;
}

export function CVPrintLayout({
  children,
  pageSize = "a4",
  typography = "sans",
  colorScheme = "slate",
  spacing = "normal",
  showToolbar = true,
  onPageSizeChange,
  onSpacingChange,
  onPrint,
  onExportPdf,
  onExportDocx,
  isExportingPdf = false,
  isExportingDocx = false,
}: CVPrintLayoutProps) {
  const [zoom, setZoom] = useState<number>(100);

  const handlePrint = () => {
    if (onPrint) {
      onPrint();
    } else {
      window.print();
    }
  };

  const zoomScale = zoom / 100;

  return (
    <div style={{ width: "100%", display: "flex", flexDirection: "column" }}>
      {/* Floating or Top Print & Layout Toolbar (Hidden on Print) */}
      {showToolbar && (
        <div
          className="no-print"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "0.75rem",
            padding: "0.75rem 1rem",
            background: "#ffffff",
            border: "1px solid var(--color-border, #e2e8f0)",
            borderRadius: "8px",
            marginBottom: "1.25rem",
            boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
          }}
        >
          {/* Left: Page Size & Spacing Controls */}
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            {/* Page Size */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
              <span style={{ fontSize: "0.82rem", color: "var(--color-text-secondary, #64748b)", fontWeight: 500 }}>
                Page Size:
              </span>
              <div style={{ display: "inline-flex", borderRadius: "6px", border: "1px solid var(--color-border, #e2e8f0)", overflow: "hidden" }}>
                <button
                  type="button"
                  onClick={() => onPageSizeChange?.("a4")}
                  style={{
                    padding: "0.25rem 0.6rem",
                    fontSize: "0.78rem",
                    fontWeight: pageSize === "a4" ? 600 : 400,
                    background: pageSize === "a4" ? "var(--color-primary-500, #2563eb)" : "transparent",
                    color: pageSize === "a4" ? "#ffffff" : "var(--color-text-primary, #0f172a)",
                    border: "none",
                    cursor: "pointer",
                  }}
                >
                  A4
                </button>
                <button
                  type="button"
                  onClick={() => onPageSizeChange?.("letter")}
                  style={{
                    padding: "0.25rem 0.6rem",
                    fontSize: "0.78rem",
                    fontWeight: pageSize === "letter" ? 600 : 400,
                    background: pageSize === "letter" ? "var(--color-primary-500, #2563eb)" : "transparent",
                    color: pageSize === "letter" ? "#ffffff" : "var(--color-text-primary, #0f172a)",
                    border: "none",
                    borderLeft: "1px solid var(--color-border, #e2e8f0)",
                    cursor: "pointer",
                  }}
                >
                  US Letter
                </button>
              </div>
            </div>

            {/* Spacing */}
            {onSpacingChange && (
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--color-text-secondary, #64748b)", fontWeight: 500 }}>
                  Density:
                </span>
                <select
                  value={spacing}
                  onChange={(e) => onSpacingChange(e.target.value as SpacingScale)}
                  style={{
                    padding: "0.25rem 0.5rem",
                    fontSize: "0.78rem",
                    borderRadius: "6px",
                    border: "1px solid var(--color-border, #e2e8f0)",
                    background: "#ffffff",
                    color: "var(--color-text-primary, #0f172a)",
                  }}
                >
                  <option value="compact">Compact</option>
                  <option value="normal">Normal</option>
                  <option value="relaxed">Relaxed</option>
                </select>
              </div>
            )}
          </div>

          {/* Right: Zoom & Print Trigger */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            {/* Zoom Controls */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.3rem" }}>
              <button
                type="button"
                aria-label="Zoom out"
                onClick={() => setZoom((z) => Math.max(50, z - 10))}
                style={{
                  background: "transparent",
                  border: "1px solid var(--color-border, #e2e8f0)",
                  borderRadius: "4px",
                  padding: "0.25rem 0.4rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <MagnifyingGlassMinus size={15} />
              </button>
              <span style={{ fontSize: "0.78rem", minWidth: "40px", textAlign: "center", fontWeight: 500 }}>
                {zoom}%
              </span>
              <button
                type="button"
                aria-label="Zoom in"
                onClick={() => setZoom((z) => Math.min(150, z + 10))}
                style={{
                  background: "transparent",
                  border: "1px solid var(--color-border, #e2e8f0)",
                  borderRadius: "4px",
                  padding: "0.25rem 0.4rem",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <MagnifyingGlassPlus size={15} />
              </button>
              {zoom !== 100 && (
                <button
                  type="button"
                  onClick={() => setZoom(100)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--color-primary-500, #2563eb)",
                    fontSize: "0.75rem",
                    cursor: "pointer",
                    textDecoration: "underline",
                  }}
                >
                  Reset
                </button>
              )}
            </div>

            {/* Export Actions */}
            {onExportPdf && (
              <Button
                variant="primary"
                size="sm"
                icon={<DownloadSimple size={16} weight="bold" />}
                onClick={onExportPdf}
                loading={isExportingPdf}
                disabled={isExportingPdf || isExportingDocx}
              >
                Download PDF
              </Button>
            )}

            {onExportDocx && (
              <Button
                variant="secondary"
                size="sm"
                icon={<DownloadSimple size={16} weight="bold" />}
                onClick={onExportDocx}
                loading={isExportingDocx}
                disabled={isExportingPdf || isExportingDocx}
              >
                Download Word (.docx)
              </Button>
            )}

            {/* Print Trigger Button */}
            <Button
              variant="ghost"
              size="sm"
              icon={<Printer size={16} weight="bold" />}
              onClick={handlePrint}
            >
              Print
            </Button>
          </div>
        </div>
      )}

      {/* Screen Page Canvas */}
      <div
        className="cv-page-container"
        style={{
          borderRadius: "10px",
          overflow: "auto",
          display: "flex",
          justifyContent: "center",
          alignItems: "flex-start",
          background: "#e2e8f0",
          padding: "2rem 1rem",
        }}
      >
        <div
          style={{
            transform: zoomScale !== 1 ? `scale(${zoomScale})` : "none",
            transformOrigin: "top center",
            transition: "transform 0.15s ease",
          }}
        >
          {/* Printable Page Sheet */}
          <div
            className={`cv-page-sheet size-${pageSize} font-${typography} spacing-${spacing} scheme-${colorScheme}`}
            style={{
              padding: "var(--cv-pad, 18mm)",
              lineHeight: "var(--cv-line-height, 1.45)",
            }}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
