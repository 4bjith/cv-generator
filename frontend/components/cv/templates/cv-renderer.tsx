"use client";

import React, { useMemo, useState } from "react";
import { CVContentSnapshot, CVPresentationSnapshot } from "@/types/cv";
import { getTemplate } from "./registry";
import { CVPrintLayout } from "./layout/cv-print-layout";
import { ColorScheme, PageSize, SpacingScale, TemplateId, TypographyStyle } from "./types";
import { TemplateGallery } from "./gallery/template-gallery";
import { Button, Modal } from "@/components/ui";
import { Palette, SquaresFour } from "@phosphor-icons/react";

export interface CVRendererProps {
  snapshot: CVContentSnapshot;
  onPresentationChange?: (presentation: CVPresentationSnapshot) => void;
  showToolbar?: boolean;
  allowTemplateSwitching?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onExportPdf?: () => void;
  onExportDocx?: () => void;
  isExportingPdf?: boolean;
  isExportingDocx?: boolean;
}

export function CVRenderer({
  snapshot,
  onPresentationChange,
  showToolbar = true,
  allowTemplateSwitching = true,
  className = "",
  style,
  onExportPdf,
  onExportDocx,
  isExportingPdf = false,
  isExportingDocx = false,
}: CVRendererProps) {
  const presentation = snapshot.presentation;
  const currentTemplateId = (presentation?.template || "modern-professional") as TemplateId;
  const templateDef = useMemo(() => getTemplate(currentTemplateId), [currentTemplateId]);

  const [isGalleryOpen, setIsGalleryOpen] = useState(false);

  // Presentation settings with sensible fallbacks
  const pageSize = (presentation?.page_size || "a4") as PageSize;
  const spacing = (presentation?.spacing || "normal") as SpacingScale;
  const colorScheme = (presentation?.color_scheme || templateDef.defaultColorScheme || "slate") as ColorScheme;
  const typography = (presentation?.typography || templateDef.defaultTypography || "sans") as TypographyStyle;

  const handleTemplateSelect = (templateId: TemplateId) => {
    const nextDef = getTemplate(templateId);
    const updated: CVPresentationSnapshot = {
      ...presentation,
      template: nextDef.id,
      typography: nextDef.defaultTypography,
      color_scheme: nextDef.defaultColorScheme,
      section_order: presentation?.section_order || [
        "basics",
        "work",
        "skills",
        "projects",
        "education",
        "certificates",
        "awards",
        "languages",
      ],
      section_visibility: presentation?.section_visibility || {
        basics: true,
        work: true,
        skills: true,
        projects: true,
        education: true,
        certificates: true,
        awards: true,
        languages: true,
      },
      item_visibility: presentation?.item_visibility || {},
    };
    onPresentationChange?.(updated);
    setIsGalleryOpen(false);
  };

  const handlePageSizeChange = (newSize: PageSize) => {
    if (!presentation) return;
    onPresentationChange?.({
      ...presentation,
      page_size: newSize,
    });
  };

  const handleSpacingChange = (newSpacing: SpacingScale) => {
    if (!presentation) return;
    onPresentationChange?.({
      ...presentation,
      spacing: newSpacing,
    });
  };

  const TemplateComponent = templateDef.component;

  return (
    <div className={`cv-renderer-wrapper ${className}`} style={style}>
      {/* Optional Top Action Bar to open Template Gallery */}
      {allowTemplateSwitching && showToolbar && (
        <div
          className="no-print"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "0.5rem 0",
            marginBottom: "0.75rem",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: "var(--color-text-secondary, #64748b)" }}>
              Template:
            </span>
            <Button
              variant="secondary"
              size="sm"
              icon={<Palette size={16} />}
              onClick={() => setIsGalleryOpen(true)}
            >
              {templateDef.name} ({templateDef.category})
            </Button>
          </div>
          <Button
            variant="ghost"
            size="sm"
            icon={<SquaresFour size={16} />}
            onClick={() => setIsGalleryOpen(true)}
          >
            Browse All 6 Templates
          </Button>
        </div>
      )}

      {/* Print & Screen Layout Container */}
      <CVPrintLayout
        pageSize={pageSize}
        typography={typography}
        colorScheme={colorScheme}
        spacing={spacing}
        showToolbar={showToolbar}
        onPageSizeChange={handlePageSizeChange}
        onSpacingChange={handleSpacingChange}
        onExportPdf={onExportPdf}
        onExportDocx={onExportDocx}
        isExportingPdf={isExportingPdf}
        isExportingDocx={isExportingDocx}
      >
        <TemplateComponent
          snapshot={snapshot}
          presentation={presentation}
          pageSize={pageSize}
          colorScheme={colorScheme}
          typography={typography}
          spacing={spacing}
        />
      </CVPrintLayout>

      {/* Template Gallery Modal */}
      <Modal
        open={isGalleryOpen}
        onClose={() => setIsGalleryOpen(false)}
        title="CV Templates Gallery"
        description="Select a template designed for your target industry or application channel. Your CV content remains completely intact."
      >
        <TemplateGallery
          selectedTemplateId={currentTemplateId}
          onSelectTemplate={handleTemplateSelect}
        />
      </Modal>
    </div>
  );
}
