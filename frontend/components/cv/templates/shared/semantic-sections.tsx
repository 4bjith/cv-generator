"use client";

import React, { ReactNode } from "react";
import {
  CVBasicsSnapshot,
  CVWorkSnapshot,
  CVEducationSnapshot,
  CVSkillSnapshot,
  CVProjectSnapshot,
  CVCertificateSnapshot,
  CVAwardSnapshot,
  CVLanguageSnapshot,
} from "@/types/cv";
import {
  formatDateRange,
  getBasicsHeadline,
  getBasicsLocation,
  getBasicsName,
  getBasicsSummary,
  isItemVisible,
} from "./helpers";

// ----------------------------------------------------------------------
// 1. Personal Header / Identity
// ----------------------------------------------------------------------
export interface PersonalHeaderProps {
  basics?: CVBasicsSnapshot | null;
  className?: string;
  style?: React.CSSProperties;
  layout?: "left" | "center" | "split" | "sidebar";
  avatarSize?: number;
  contactSeparator?: ReactNode;
}

export function PersonalHeader({
  basics,
  className = "",
  style,
  layout = "left",
  avatarSize = 64,
  contactSeparator = " • ",
}: PersonalHeaderProps) {
  if (!basics) return null;
  const name = getBasicsName(basics);
  const headline = getBasicsHeadline(basics);
  const location = getBasicsLocation(basics);
  const profiles = basics.profiles || [];

  if (!name && !headline && !basics.email && !basics.phone) return null;

  const contactItems: ReactNode[] = [];
  if (basics.email) {
    contactItems.push(
      <a key="email" href={`mailto:${basics.email}`} className="cv-contact-link">
        {basics.email}
      </a>
    );
  }
  if (basics.phone) {
    contactItems.push(
      <a key="phone" href={`tel:${basics.phone}`} className="cv-contact-link">
        {basics.phone}
      </a>
    );
  }
  if (location) {
    contactItems.push(<span key="location">{location}</span>);
  }
  if (basics.url) {
    contactItems.push(
      <a key="url" href={basics.url} target="_blank" rel="noopener noreferrer" className="cv-contact-link">
        {basics.url.replace(/^https?:\/\//, "")}
      </a>
    );
  }
  profiles.forEach((p, idx) => {
    if (p.url) {
      contactItems.push(
        <a key={`profile-${idx}`} href={p.url} target="_blank" rel="noopener noreferrer" className="cv-contact-link">
          {p.network ? `${p.network}: ${p.username || p.url.replace(/^https?:\/\//, "")}` : p.url}
        </a>
      );
    }
  });

  return (
    <header className={`cv-header cv-header-${layout} ${className}`} style={style}>
      {layout === "center" ? (
        <div style={{ textAlign: "center" }}>
          {basics.image && (
            <div style={{ marginBottom: "0.75rem", display: "flex", justifyContent: "center" }}>
              <img
                src={basics.image}
                alt={name}
                style={{
                  width: `${avatarSize}px`,
                  height: `${avatarSize}px`,
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: "2px solid var(--cv-accent, #2563eb)",
                }}
              />
            </div>
          )}
          <h1 style={{ margin: 0, fontSize: "2rem", fontWeight: 700, letterSpacing: "-0.015em", color: "var(--cv-heading, #0f172a)" }}>
            {name || "Candidate Name"}
          </h1>
          {headline && (
            <p style={{ margin: "0.25rem 0 0.5rem", fontSize: "1.05rem", fontWeight: 500, color: "var(--cv-accent, #2563eb)" }}>
              {headline}
            </p>
          )}
          {contactItems.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "0.35rem 0.5rem", fontSize: "0.85rem", color: "var(--cv-muted, #64748b)" }}>
              {contactItems.map((item, i) => (
                <React.Fragment key={i}>
                  {i > 0 && <span aria-hidden="true" style={{ opacity: 0.5 }}>{contactSeparator}</span>}
                  {item}
                </React.Fragment>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem" }}>
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: 0, fontSize: "1.9rem", fontWeight: 700, letterSpacing: "-0.015em", color: "var(--cv-heading, #0f172a)" }}>
              {name || "Candidate Name"}
            </h1>
            {headline && (
              <p style={{ margin: "0.2rem 0 0.45rem", fontSize: "1rem", fontWeight: 500, color: "var(--cv-accent, #2563eb)" }}>
                {headline}
              </p>
            )}
            {contactItems.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem 0.5rem", fontSize: "0.82rem", color: "var(--cv-muted, #64748b)" }}>
                {contactItems.map((item, i) => (
                  <React.Fragment key={i}>
                    {i > 0 && <span aria-hidden="true" style={{ opacity: 0.5 }}>{contactSeparator}</span>}
                    {item}
                  </React.Fragment>
                ))}
              </div>
            )}
          </div>
          {basics.image && (
            <div>
              <img
                src={basics.image}
                alt={name}
                style={{
                  width: `${avatarSize}px`,
                  height: `${avatarSize}px`,
                  borderRadius: "50%",
                  objectFit: "cover",
                  border: "2px solid var(--cv-accent, #2563eb)",
                }}
              />
            </div>
          )}
        </div>
      )}
    </header>
  );
}

// ----------------------------------------------------------------------
// 2. Summary
// ----------------------------------------------------------------------
export interface SummarySectionProps {
  basics?: CVBasicsSnapshot | null;
  title?: string;
  className?: string;
  style?: React.CSSProperties;
  titleStyle?: React.CSSProperties;
}

export function SummarySection({
  basics,
  title = "Professional Summary",
  className = "",
  style,
  titleStyle,
}: SummarySectionProps) {
  const summary = getBasicsSummary(basics);
  if (!summary || !summary.trim()) return null;

  return (
    <section className={`cv-section cv-summary ${className}`} style={style}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <p style={{ margin: 0, lineHeight: "inherit", color: "var(--cv-text, #334155)", whiteSpace: "pre-line" }}>
        {summary}
      </p>
    </section>
  );
}

// ----------------------------------------------------------------------
// 3. Work Experience
// ----------------------------------------------------------------------
export interface WorkSectionProps {
  work?: CVWorkSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
  showMetrics?: boolean;
  showTech?: boolean;
}

export function WorkSection({
  work = [],
  itemVisibility,
  title = "Work Experience",
  className = "",
  titleStyle,
  showMetrics = true,
  showTech = true,
}: WorkSectionProps) {
  const visible = work.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-work ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--cv-item-gap, 0.85rem)" }}>
        {visible.map((exp, idx) => {
          const dateStr = formatDateRange(exp.startDate || exp.start_date, exp.endDate || exp.end_date, exp.is_current);
          const bullets = exp.highlights || exp.responsibilities || [];
          const achievements = exp.achievements || [];
          const allBullets = Array.from(new Set([...bullets, ...achievements]));
          const metrics = exp.metrics || [];
          const techs = exp.technologies || [];

          return (
            <article key={exp.id || idx} className="cv-item cv-work-item">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "0.25rem" }}>
                <div>
                  <strong style={{ fontSize: "1.02em", color: "var(--cv-heading, #0f172a)" }}>
                    {exp.position || "Role Title"}
                  </strong>
                  {(exp.name || exp.company) && (
                    <span style={{ color: "var(--cv-muted, #64748b)", marginLeft: "0.35rem", fontWeight: 500 }}>
                      — {exp.name || exp.company}
                    </span>
                  )}
                  {exp.location && (
                    <span style={{ color: "var(--cv-muted, #64748b)", fontSize: "0.85em", marginLeft: "0.35rem" }}>
                      ({exp.location})
                    </span>
                  )}
                </div>
                {dateStr && (
                  <span style={{ fontSize: "0.88em", color: "var(--cv-muted, #64748b)", fontWeight: 500 }}>
                    {dateStr}
                  </span>
                )}
              </div>

              {(exp.summary || exp.description) && (
                <p style={{ margin: "0.25rem 0", color: "var(--cv-text, #334155)", fontSize: "0.95em" }}>
                  {exp.summary || exp.description}
                </p>
              )}

              {allBullets.length > 0 && (
                <ul style={{ margin: "0.3rem 0 0", paddingLeft: "1.2rem", color: "var(--cv-text, #334155)" }}>
                  {allBullets.map((b, bIdx) => (
                    <li key={bIdx} style={{ marginBottom: "0.2rem" }}>
                      {b}
                    </li>
                  ))}
                </ul>
              )}

              {/* Metrics Highlights */}
              {showMetrics && metrics.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.4rem" }}>
                  {metrics.map((m, mIdx) => (
                    <span
                      key={mIdx}
                      style={{
                        fontSize: "0.78em",
                        padding: "0.15rem 0.5rem",
                        background: "var(--cv-accent-muted, #f1f5f9)",
                        color: "var(--cv-accent, #2563eb)",
                        borderRadius: "4px",
                        fontWeight: 600,
                      }}
                    >
                      {m.value || m.metric_name}: {m.context || m.label || "Impact"}
                    </span>
                  ))}
                </div>
              )}

              {/* Technologies */}
              {showTech && techs.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "0.3rem", marginTop: "0.35rem", fontSize: "0.8em", color: "var(--cv-muted, #64748b)" }}>
                  <span style={{ fontWeight: 600 }}>Technologies:</span>
                  {techs.join(" • ")}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

// ----------------------------------------------------------------------
// 4. Education
// ----------------------------------------------------------------------
export interface EducationSectionProps {
  education?: CVEducationSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
}

export function EducationSection({
  education = [],
  itemVisibility,
  title = "Education",
  className = "",
  titleStyle,
}: EducationSectionProps) {
  const visible = education.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-education ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--cv-item-gap, 0.75rem)" }}>
        {visible.map((edu, idx) => {
          const dateStr = formatDateRange(edu.startDate || edu.start_date, edu.endDate || edu.end_date);
          const degreeStr = [edu.studyType || edu.degree, edu.area || edu.field_of_study].filter(Boolean).join(" in ");

          return (
            <article key={edu.id || idx} className="cv-item cv-edu-item">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "0.25rem" }}>
                <div>
                  <strong style={{ fontSize: "1em", color: "var(--cv-heading, #0f172a)" }}>
                    {edu.institution || "University / School"}
                  </strong>
                  {degreeStr && (
                    <div style={{ color: "var(--cv-text, #334155)", fontSize: "0.95em", fontWeight: 500 }}>
                      {degreeStr}
                    </div>
                  )}
                </div>
                {dateStr && (
                  <span style={{ fontSize: "0.88em", color: "var(--cv-muted, #64748b)", fontWeight: 500 }}>
                    {dateStr}
                  </span>
                )}
              </div>

              {(edu.score || edu.grade) && (
                <div style={{ fontSize: "0.85em", color: "var(--cv-muted, #64748b)", marginTop: "0.15rem" }}>
                  Honors / GPA: <strong>{edu.score || edu.grade}</strong>
                </div>
              )}

              {edu.courses && edu.courses.length > 0 && (
                <div style={{ fontSize: "0.82em", color: "var(--cv-muted, #64748b)", marginTop: "0.2rem" }}>
                  Relevant Courses: {edu.courses.join(", ")}
                </div>
              )}

              {edu.achievements && edu.achievements.length > 0 && (
                <ul style={{ margin: "0.2rem 0 0", paddingLeft: "1.2rem", fontSize: "0.9em", color: "var(--cv-text, #334155)" }}>
                  {edu.achievements.map((ach, aIdx) => (
                    <li key={aIdx}>{ach}</li>
                  ))}
                </ul>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

// ----------------------------------------------------------------------
// 5. Skills
// ----------------------------------------------------------------------
export interface SkillsSectionProps {
  skills?: CVSkillSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
  layout?: "tags" | "categorized" | "inline";
}

export function SkillsSection({
  skills = [],
  itemVisibility,
  title = "Skills & Proficiencies",
  className = "",
  titleStyle,
  layout = "categorized",
}: SkillsSectionProps) {
  const visible = skills.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  // Group by category if present
  const categories: Record<string, CVSkillSnapshot[]> = {};
  const unclassified: CVSkillSnapshot[] = [];

  visible.forEach((s) => {
    const cat = s.category || "General";
    if (s.category) {
      if (!categories[cat]) categories[cat] = [];
      categories[cat].push(s);
    } else {
      unclassified.push(s);
    }
  });

  const hasCategories = Object.keys(categories).length > 0;

  return (
    <section className={`cv-section cv-skills ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}

      {layout === "categorized" && hasCategories ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
          {Object.entries(categories).map(([cat, list]) => (
            <div key={cat} style={{ fontSize: "0.92em" }}>
              <strong style={{ color: "var(--cv-heading, #0f172a)", marginRight: "0.4rem" }}>
                {cat}:
              </strong>
              <span style={{ color: "var(--cv-text, #334155)" }}>
                {list.map((item) => item.name).filter(Boolean).join(", ")}
              </span>
            </div>
          ))}
          {unclassified.length > 0 && (
            <div style={{ fontSize: "0.92em" }}>
              <strong style={{ color: "var(--cv-heading, #0f172a)", marginRight: "0.4rem" }}>
                Other:
              </strong>
              <span style={{ color: "var(--cv-text, #334155)" }}>
                {unclassified.map((item) => item.name).filter(Boolean).join(", ")}
              </span>
            </div>
          )}
        </div>
      ) : layout === "tags" ? (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
          {visible.map((s, idx) => (
            <span
              key={s.id || idx}
              style={{
                fontSize: "0.82em",
                padding: "0.2rem 0.55rem",
                background: "var(--cv-accent-muted, #f1f5f9)",
                color: "var(--cv-heading, #0f172a)",
                borderRadius: "4px",
                border: "1px solid var(--cv-border, #e2e8f0)",
                fontWeight: 500,
              }}
            >
              {s.name}
              {s.proficiency && ` (${s.proficiency})`}
            </span>
          ))}
        </div>
      ) : (
        <p style={{ margin: 0, fontSize: "0.92em", color: "var(--cv-text, #334155)" }}>
          {visible.map((s) => s.name).filter(Boolean).join(" • ")}
        </p>
      )}
    </section>
  );
}

// ----------------------------------------------------------------------
// 6. Projects
// ----------------------------------------------------------------------
export interface ProjectsSectionProps {
  projects?: CVProjectSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
}

export function ProjectsSection({
  projects = [],
  itemVisibility,
  title = "Key Projects",
  className = "",
  titleStyle,
}: ProjectsSectionProps) {
  const visible = projects.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-projects ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "var(--cv-item-gap, 0.75rem)" }}>
        {visible.map((proj, idx) => {
          const bullets = proj.highlights || proj.responsibilities || [];
          const techs = proj.technologies || proj.keywords || [];
          const projectUrl = proj.url || proj.live_url || proj.repository_url;

          return (
            <article key={proj.id || idx} className="cv-item cv-project-item">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", flexWrap: "wrap", gap: "0.25rem" }}>
                <div>
                  <strong style={{ fontSize: "1em", color: "var(--cv-heading, #0f172a)" }}>
                    {proj.name || "Project Title"}
                  </strong>
                  {proj.role && (
                    <span style={{ color: "var(--cv-muted, #64748b)", fontSize: "0.9em", marginLeft: "0.35rem" }}>
                      — {proj.role}
                    </span>
                  )}
                </div>
                {projectUrl && (
                  <a
                    href={projectUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ fontSize: "0.82em", color: "var(--cv-accent, #2563eb)", fontWeight: 500 }}
                  >
                    View Project ↗
                  </a>
                )}
              </div>

              {(proj.description || proj.solution) && (
                <p style={{ margin: "0.2rem 0", color: "var(--cv-text, #334155)", fontSize: "0.92em" }}>
                  {proj.description || proj.solution}
                </p>
              )}

              {bullets.length > 0 && (
                <ul style={{ margin: "0.25rem 0 0", paddingLeft: "1.2rem", fontSize: "0.9em", color: "var(--cv-text, #334155)" }}>
                  {bullets.map((b, bIdx) => (
                    <li key={bIdx}>{b}</li>
                  ))}
                </ul>
              )}

              {techs.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginTop: "0.3rem", fontSize: "0.78em", color: "var(--cv-muted, #64748b)" }}>
                  <span style={{ fontWeight: 600 }}>Stack:</span>
                  {techs.join(" • ")}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}

// ----------------------------------------------------------------------
// 7. Certifications
// ----------------------------------------------------------------------
export interface CertificationsSectionProps {
  certificates?: CVCertificateSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
}

export function CertificationsSection({
  certificates = [],
  itemVisibility,
  title = "Certifications",
  className = "",
  titleStyle,
}: CertificationsSectionProps) {
  const visible = certificates.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-certificates ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem" }}>
        {visible.map((cert, idx) => (
          <div key={cert.id || idx} className="cv-item" style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <div>
              <strong style={{ fontSize: "0.95em", color: "var(--cv-heading, #0f172a)" }}>
                {cert.name}
              </strong>
              {cert.issuer && (
                <span style={{ color: "var(--cv-muted, #64748b)", marginLeft: "0.35rem", fontSize: "0.9em" }}>
                  — {cert.issuer}
                </span>
              )}
            </div>
            {(cert.date || cert.issue_date) && (
              <span style={{ fontSize: "0.85em", color: "var(--cv-muted, #64748b)" }}>
                {cert.date || cert.issue_date}
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

// ----------------------------------------------------------------------
// 8. Awards & Honors
// ----------------------------------------------------------------------
export interface AwardsSectionProps {
  awards?: CVAwardSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
}

export function AwardsSection({
  awards = [],
  itemVisibility,
  title = "Honors & Awards",
  className = "",
  titleStyle,
}: AwardsSectionProps) {
  const visible = awards.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-awards ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {visible.map((award, idx) => (
          <div key={award.id || idx} className="cv-item">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <strong style={{ fontSize: "0.95em", color: "var(--cv-heading, #0f172a)" }}>
                {award.title}
              </strong>
              {award.date && (
                <span style={{ fontSize: "0.85em", color: "var(--cv-muted, #64748b)" }}>
                  {award.date}
                </span>
              )}
            </div>
            {award.awarder && (
              <div style={{ fontSize: "0.88em", color: "var(--cv-muted, #64748b)" }}>
                Awarded by {award.awarder}
              </div>
            )}
            {(award.summary || award.description) && (
              <p style={{ margin: "0.15rem 0 0", fontSize: "0.88em", color: "var(--cv-text, #334155)" }}>
                {award.summary || award.description}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}

// ----------------------------------------------------------------------
// 9. Languages
// ----------------------------------------------------------------------
export interface LanguagesSectionProps {
  languages?: CVLanguageSnapshot[];
  itemVisibility?: Record<string, boolean>;
  title?: string;
  className?: string;
  titleStyle?: React.CSSProperties;
}

export function LanguagesSection({
  languages = [],
  itemVisibility,
  title = "Languages",
  className = "",
  titleStyle,
}: LanguagesSectionProps) {
  const visible = languages.filter((item) => isItemVisible(item.id, itemVisibility));
  if (visible.length === 0) return null;

  return (
    <section className={`cv-section cv-languages ${className}`}>
      {title && (
        <h2 className="cv-section-title" style={titleStyle}>
          {title}
        </h2>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem 0.8rem", fontSize: "0.92em" }}>
        {visible.map((l, idx) => {
          const lang = l.language || l.name;
          const level = l.fluency || l.proficiency;
          return (
            <span key={l.id || idx} style={{ color: "var(--cv-text, #334155)" }}>
              <strong style={{ color: "var(--cv-heading, #0f172a)" }}>{lang}</strong>
              {level && <span style={{ color: "var(--cv-muted, #64748b)" }}> ({level})</span>}
            </span>
          );
        })}
      </div>
    </section>
  );
}
