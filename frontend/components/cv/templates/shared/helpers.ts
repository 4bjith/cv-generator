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

export const DEFAULT_SECTION_ORDER = [
  "basics",
  "work",
  "skills",
  "projects",
  "education",
  "certificates",
  "awards",
  "languages",
];

export function getBasicsName(basics?: CVBasicsSnapshot | null): string {
  if (!basics) return "";
  if (basics.name && basics.name.trim()) return basics.name.trim();
  const parts = [basics.first_name, basics.last_name].filter(Boolean);
  if (parts.length > 0) return parts.join(" ").trim();
  return "";
}

export function getBasicsHeadline(basics?: CVBasicsSnapshot | null): string {
  if (!basics) return "";
  return basics.label || basics.professional_headline || basics.primary_title || "";
}

export function getBasicsSummary(basics?: CVBasicsSnapshot | null): string {
  if (!basics) return "";
  return basics.summary || basics.base_summary || "";
}

export function getBasicsLocation(basics?: CVBasicsSnapshot | null): string {
  if (!basics) return "";
  if (basics.location) {
    const loc = basics.location;
    const parts = [loc.city, loc.region, loc.country || loc.countryCode].filter(Boolean);
    if (parts.length > 0) return parts.join(", ");
  }
  const parts = [basics.city, basics.state, basics.country].filter(Boolean);
  return parts.join(", ");
}

export function formatDateRange(
  startDate?: string | null,
  endDate?: string | null,
  isCurrent?: boolean
): string {
  if (!startDate && !endDate) return "";
  const startStr = startDate ? formatMonthYear(startDate) : "";
  if (isCurrent) {
    return startStr ? `${startStr} – Present` : "Present";
  }
  const endStr = endDate ? formatMonthYear(endDate) : "";
  if (startStr && endStr) return `${startStr} – ${endStr}`;
  if (startStr) return startStr;
  return endStr;
}

export function formatMonthYear(dateStr: string): string {
  if (!dateStr) return "";
  // If already in YYYY-MM or YYYY format
  if (/^\d{4}$/.test(dateStr)) return dateStr;
  try {
    const parts = dateStr.split("-");
    if (parts.length >= 2) {
      const year = parseInt(parts[0], 10);
      const month = parseInt(parts[1], 10) - 1;
      const d = new Date(year, month);
      if (!isNaN(d.getTime())) {
        return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
      }
    }
    const d = new Date(dateStr);
    if (!isNaN(d.getTime())) {
      return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
    }
  } catch {
    // fallback
  }
  return dateStr;
}

export function isItemVisible(itemId?: string | null, itemVisibility?: Record<string, boolean>): boolean {
  if (!itemId) return true;
  if (!itemVisibility) return true;
  return itemVisibility[itemId] !== false;
}

export function isSectionVisible(
  secKey: string,
  sectionVisibility?: Record<string, boolean>,
  hasContent: boolean = true
): boolean {
  if (!hasContent) return false;
  if (!sectionVisibility) return true;
  return sectionVisibility[secKey] !== false;
}

export function getVisibleWork(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVWorkSnapshot[] {
  const items = snapshot.work || snapshot.experiences || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleEducation(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVEducationSnapshot[] {
  const items = snapshot.education || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleSkills(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVSkillSnapshot[] {
  const items = snapshot.skills || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleProjects(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVProjectSnapshot[] {
  const items = snapshot.projects || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleCertificates(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVCertificateSnapshot[] {
  const items = snapshot.certificates || snapshot.certifications || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleAwards(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVAwardSnapshot[] {
  const items = snapshot.awards || snapshot.achievements || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getVisibleLanguages(
  snapshot: CVContentSnapshot,
  itemVisibility?: Record<string, boolean>
): CVLanguageSnapshot[] {
  const items = snapshot.languages || [];
  return items.filter((item) => isItemVisible(item.id, itemVisibility));
}

export function getResolvedSectionOrder(presentation?: CVPresentationSnapshot): string[] {
  const customOrder = presentation?.section_order || DEFAULT_SECTION_ORDER;
  const existing = new Set(customOrder);
  const full = [...customOrder];
  for (const s of DEFAULT_SECTION_ORDER) {
    if (!existing.has(s)) full.push(s);
  }
  return full;
}
