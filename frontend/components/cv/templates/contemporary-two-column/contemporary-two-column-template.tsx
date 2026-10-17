"use client";

import React from "react";
import { CVTemplateProps } from "../types";
import {
  AwardsSection,
  CertificationsSection,
  EducationSection,
  LanguagesSection,
  ProjectsSection,
  SkillsSection,
  SummarySection,
  WorkSection,
} from "../shared/semantic-sections";
import {
  getBasicsHeadline,
  getBasicsLocation,
  getBasicsName,
  getResolvedSectionOrder,
  getVisibleAwards,
  getVisibleCertificates,
  getVisibleEducation,
  getVisibleLanguages,
  getVisibleProjects,
  getVisibleSkills,
  getVisibleWork,
  isSectionVisible,
} from "../shared/helpers";

export function ContemporaryTwoColumnTemplate({ snapshot, presentation }: CVTemplateProps) {
  const { basics } = snapshot;
  const itemVis = presentation?.item_visibility;
  const secVis = presentation?.section_visibility;
  const sectionOrder = getResolvedSectionOrder(presentation);

  const name = getBasicsName(basics);
  const headline = getBasicsHeadline(basics);
  const location = getBasicsLocation(basics);

  const workList = getVisibleWork(snapshot, itemVis);
  const eduList = getVisibleEducation(snapshot, itemVis);
  const skillsList = getVisibleSkills(snapshot, itemVis);
  const projectsList = getVisibleProjects(snapshot, itemVis);
  const certList = getVisibleCertificates(snapshot, itemVis);
  const awardsList = getVisibleAwards(snapshot, itemVis);
  const langList = getVisibleLanguages(snapshot, itemVis);

  const mainTitleStyle: React.CSSProperties = {
    fontSize: "0.95rem",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.05em",
    color: "var(--cv-heading, #0f172a)",
    borderBottom: "2px solid var(--cv-accent, #4f46e5)",
    paddingBottom: "0.25rem",
    marginBottom: "0.75rem",
  };

  const sidebarTitleStyle: React.CSSProperties = {
    fontSize: "0.85rem",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "var(--cv-heading, #0f172a)",
    borderBottom: "1.5px solid var(--cv-border, #cbd5e1)",
    paddingBottom: "0.2rem",
    marginBottom: "0.5rem",
  };

  // Main column renders experience, projects, summary, awards
  const renderMainSection = (secKey: string) => {
    switch (secKey) {
      case "basics":
        if (!isSectionVisible("basics", secVis, !!basics?.summary || !!basics?.base_summary)) return null;
        return (
          <SummarySection
            key="summary"
            basics={basics}
            title="Profile Summary"
            titleStyle={mainTitleStyle}
          />
        );
      case "work":
        if (!isSectionVisible("work", secVis, workList.length > 0)) return null;
        return (
          <WorkSection
            key="work"
            work={workList}
            itemVisibility={itemVis}
            title="Experience"
            titleStyle={mainTitleStyle}
          />
        );
      case "projects":
        if (!isSectionVisible("projects", secVis, projectsList.length > 0)) return null;
        return (
          <ProjectsSection
            key="projects"
            projects={projectsList}
            itemVisibility={itemVis}
            title="Key Projects"
            titleStyle={mainTitleStyle}
          />
        );
      case "awards":
        if (!isSectionVisible("awards", secVis, awardsList.length > 0)) return null;
        return (
          <AwardsSection
            key="awards"
            awards={awardsList}
            itemVisibility={itemVis}
            title="Achievements"
            titleStyle={mainTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  // Sidebar renders contact, skills, education, certificates, languages
  const renderSidebarSection = (secKey: string) => {
    switch (secKey) {
      case "skills":
        if (!isSectionVisible("skills", secVis, skillsList.length > 0)) return null;
        return (
          <SkillsSection
            key="skills"
            skills={skillsList}
            itemVisibility={itemVis}
            title="Skills"
            titleStyle={sidebarTitleStyle}
            layout="tags"
          />
        );
      case "education":
        if (!isSectionVisible("education", secVis, eduList.length > 0)) return null;
        return (
          <EducationSection
            key="education"
            education={eduList}
            itemVisibility={itemVis}
            title="Education"
            titleStyle={sidebarTitleStyle}
          />
        );
      case "certificates":
        if (!isSectionVisible("certificates", secVis, certList.length > 0)) return null;
        return (
          <CertificationsSection
            key="certificates"
            certificates={certList}
            itemVisibility={itemVis}
            title="Certifications"
            titleStyle={sidebarTitleStyle}
          />
        );
      case "languages":
        if (!isSectionVisible("languages", secVis, langList.length > 0)) return null;
        return (
          <LanguagesSection
            key="languages"
            languages={langList}
            itemVisibility={itemVis}
            title="Languages"
            titleStyle={sidebarTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="template-contemporary-two-column">
      {/* Prominent Header Banner */}
      <header
        style={{
          borderBottom: "2px solid var(--cv-border, #e2e8f0)",
          paddingBottom: "1.25rem",
          marginBottom: "1.5rem",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "1.5rem",
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: "2.1rem", fontWeight: 800, letterSpacing: "-0.02em", color: "var(--cv-heading, #0f172a)" }}>
            {name || "Candidate Name"}
          </h1>
          {headline && (
            <p style={{ margin: "0.25rem 0 0", fontSize: "1.05rem", fontWeight: 600, color: "var(--cv-accent, #4f46e5)" }}>
              {headline}
            </p>
          )}
        </div>
        {basics?.image && (
          <img
            src={basics.image}
            alt={name}
            style={{
              width: "72px",
              height: "72px",
              borderRadius: "12px",
              objectFit: "cover",
              border: "2px solid var(--cv-accent, #4f46e5)",
            }}
          />
        )}
      </header>

      {/* Asymmetric Two-Column Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "220px 1fr",
          gap: "1.75rem",
          alignItems: "start",
        }}
      >
        {/* Left Sidebar */}
        <aside
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1.25rem",
            background: "var(--cv-accent-muted, #f8fafc)",
            padding: "1rem",
            borderRadius: "8px",
            border: "1px solid var(--cv-border, #e2e8f0)",
          }}
        >
          {/* Contact Details */}
          <div>
            <h3 style={sidebarTitleStyle}>Contact</h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", fontSize: "0.82rem", color: "var(--cv-text, #334155)" }}>
              {basics?.email && (
                <a href={`mailto:${basics.email}`} style={{ wordBreak: "break-all", color: "inherit" }}>
                  ✉ {basics.email}
                </a>
              )}
              {basics?.phone && <span>📞 {basics.phone}</span>}
              {location && <span>📍 {location}</span>}
              {basics?.url && (
                <a href={basics.url} target="_blank" rel="noopener noreferrer" style={{ wordBreak: "break-all", color: "var(--cv-accent, #4f46e5)" }}>
                  🌐 {basics.url.replace(/^https?:\/\//, "")}
                </a>
              )}
              {(basics?.profiles || []).map((p, idx) => (
                <a key={idx} href={p.url || "#"} target="_blank" rel="noopener noreferrer" style={{ wordBreak: "break-all", color: "var(--cv-accent, #4f46e5)" }}>
                  ↗ {p.network ? `${p.network}: ${p.username || ""}` : p.url}
                </a>
              ))}
            </div>
          </div>

          {/* Sidebar ordered sections */}
          {sectionOrder.map((secKey) => renderSidebarSection(secKey))}
        </aside>

        {/* Right Main Column */}
        <main style={{ display: "flex", flexDirection: "column", gap: "var(--cv-sec-gap, 1.4rem)" }}>
          {sectionOrder.map((secKey) => renderMainSection(secKey))}
        </main>
      </div>
    </div>
  );
}
