import { CVContentSnapshot, CVPresentationSnapshot } from "@/types/cv";

export type TemplateId =
  | "modern-professional"
  | "classic-executive"
  | "ats-minimal"
  | "technical-developer"
  | "contemporary-two-column"
  | "academic-research"
  | string;

export type PageSize = "a4" | "letter";
export type TypographyStyle = "sans" | "serif" | "mono";
export type ColorScheme = "slate" | "blue" | "emerald" | "burgundy" | "amber" | "monochrome";
export type SpacingScale = "compact" | "normal" | "relaxed";

export interface CVTemplateProps {
  snapshot: CVContentSnapshot;
  presentation?: CVPresentationSnapshot;
  pageSize?: PageSize;
  colorScheme?: ColorScheme | string;
  typography?: TypographyStyle | string;
  spacing?: SpacingScale | string;
  isPrint?: boolean;
}

export interface TemplateDefinition {
  id: TemplateId;
  aliases: string[];
  name: string;
  category: "Professional" | "Executive" | "Technical" | "ATS" | "Creative" | "Academic";
  description: string;
  recommendedFor: string;
  defaultTypography: TypographyStyle;
  defaultColorScheme: ColorScheme;
  layoutType: "single-column" | "two-column" | "academic-dense";
  features: string[];
  component: React.ComponentType<CVTemplateProps>;
}
