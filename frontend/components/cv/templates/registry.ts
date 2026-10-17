import { TemplateDefinition } from "./types";
import { ModernProfessionalTemplate } from "./modern-professional/modern-professional-template";
import { ClassicExecutiveTemplate } from "./classic-executive/classic-executive-template";
import { AtsMinimalTemplate } from "./ats-minimal/ats-minimal-template";
import { TechnicalDeveloperTemplate } from "./technical-developer/technical-developer-template";
import { ContemporaryTwoColumnTemplate } from "./contemporary-two-column/contemporary-two-column-template";
import { AcademicResearchTemplate } from "./academic-research/academic-research-template";

const TEMPLATE_REGISTRY = new Map<string, TemplateDefinition>();
const TEMPLATE_LIST: TemplateDefinition[] = [];

export function registerTemplate(template: TemplateDefinition) {
  TEMPLATE_REGISTRY.set(template.id.toLowerCase(), template);
  template.aliases.forEach((alias) => {
    TEMPLATE_REGISTRY.set(alias.toLowerCase(), template);
  });
  const existingIdx = TEMPLATE_LIST.findIndex((t) => t.id === template.id);
  if (existingIdx >= 0) {
    TEMPLATE_LIST[existingIdx] = template;
  } else {
    TEMPLATE_LIST.push(template);
  }
}

// ----------------------------------------------------------------------
// Built-in Launch Templates
// ----------------------------------------------------------------------

export const MODERN_PROFESSIONAL: TemplateDefinition = {
  id: "modern-professional",
  aliases: ["modern", "corporate", "professional"],
  name: "Modern Professional",
  category: "Professional",
  description: "Clean, contemporary single-column layout with strong typography and subtle sapphire accents.",
  recommendedFor: "General corporate, business, management, consulting, and professional careers.",
  defaultTypography: "sans",
  defaultColorScheme: "slate",
  layoutType: "single-column",
  features: ["Single-column clean hierarchy", "Accent divider bars", "Metric badges", "Corporate ready"],
  component: ModernProfessionalTemplate,
};

export const CLASSIC_EXECUTIVE: TemplateDefinition = {
  id: "classic-executive",
  aliases: ["executive", "classic", "leadership"],
  name: "Classic Executive",
  category: "Executive",
  description: "Formal, polished typography with serif headings, refined double divider rules, and leadership focus.",
  recommendedFor: "Executives, VPs, directors, senior managers, legal, and finance professionals.",
  defaultTypography: "serif",
  defaultColorScheme: "slate",
  layoutType: "single-column",
  features: ["Editorial serif typography", "Centered dignified header", "Leadership progression", "Conservative styling"],
  component: ClassicExecutiveTemplate,
};

export const ATS_MINIMAL: TemplateDefinition = {
  id: "ats-minimal",
  aliases: ["minimal", "ats", "ats-simple"],
  name: "ATS-Friendly Minimal",
  category: "ATS",
  description: "Text-first, linear single-column design engineered for maximum ATS parser readability and compliance.",
  recommendedFor: "Online applications, automated screening portals (Workday, Taleo, Greenhouse, Lever).",
  defaultTypography: "sans",
  defaultColorScheme: "monochrome",
  layoutType: "single-column",
  features: ["100% linear text structure", "Standard headings & bullets", "High contrast monochrome", "Zero parsing friction"],
  component: AtsMinimalTemplate,
};

export const TECHNICAL_DEVELOPER: TemplateDefinition = {
  id: "technical-developer",
  aliases: ["technical", "developer", "software-engineer", "dev"],
  name: "Technical / Software Developer",
  category: "Technical",
  description: "Clear technical skills hierarchy, systems project highlights, tech stack badges, and monospace accents.",
  recommendedFor: "Software engineers, systems architects, DevOps, cloud practitioners, and tech leads.",
  defaultTypography: "mono",
  defaultColorScheme: "blue",
  layoutType: "single-column",
  features: ["Categorized skills matrix", "Monospace code tags", "Performance metric callouts", "GitHub & live links"],
  component: TechnicalDeveloperTemplate,
};

export const CONTEMPORARY_TWO_COLUMN: TemplateDefinition = {
  id: "contemporary-two-column",
  aliases: ["two-column", "contemporary", "sidebar"],
  name: "Contemporary Two-Column",
  category: "Creative",
  description: "Dynamic asymmetric two-column design with a dedicated sidebar for contact, skills, and education.",
  recommendedFor: "Modern digital roles, product managers, designers, marketing, and cross-functional teams.",
  defaultTypography: "sans",
  defaultColorScheme: "blue",
  layoutType: "two-column",
  features: ["Asymmetric sidebar & main column", "Compact skill pills", "Visual contrast", "Print-safe flow"],
  component: ContemporaryTwoColumnTemplate,
};

export const ACADEMIC_RESEARCH: TemplateDefinition = {
  id: "academic-research",
  aliases: ["academic", "research", "scholar", "cv"],
  name: "Academic / Research",
  category: "Academic",
  description: "Formal, scholarly, content-dense layout designed for academic CVs, publications, research, and grants.",
  recommendedFor: "Professors, researchers, scientists, PhD candidates, scholars, and academic fellowship applicants.",
  defaultTypography: "serif",
  defaultColorScheme: "slate",
  layoutType: "academic-dense",
  features: ["Scholarly serif typography", "Education-first hierarchy", "Publications & grants", "Multi-page seamless flow"],
  component: AcademicResearchTemplate,
};

// Register all 6 default templates
registerTemplate(MODERN_PROFESSIONAL);
registerTemplate(CLASSIC_EXECUTIVE);
registerTemplate(ATS_MINIMAL);
registerTemplate(TECHNICAL_DEVELOPER);
registerTemplate(CONTEMPORARY_TWO_COLUMN);
registerTemplate(ACADEMIC_RESEARCH);

export function getAllTemplates(): TemplateDefinition[] {
  return [...TEMPLATE_LIST];
}

export function getTemplate(id?: string | null): TemplateDefinition {
  if (!id) return MODERN_PROFESSIONAL;
  const key = id.toLowerCase().trim();
  const found = TEMPLATE_REGISTRY.get(key);
  if (found) return found;
  return MODERN_PROFESSIONAL;
}
