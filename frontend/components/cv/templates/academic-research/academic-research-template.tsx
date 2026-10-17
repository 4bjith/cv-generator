"use client";

import React from "react";
import { CVTemplateProps } from "../types";
import {
  AwardsSection,
  CertificationsSection,
  EducationSection,
  LanguagesSection,
  PersonalHeader,
  ProjectsSection,
  SkillsSection,
  SummarySection,
  WorkSection,
} from "../shared/semantic-sections";
import {
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

export function AcademicResearchTemplate({ snapshot, presentation }: CVTemplateProps) {
  const { basics } = snapshot;
  const itemVis = presentation?.item_visibility;
  const secVis = presentation?.section_visibility;
  const sectionOrder = getResolvedSectionOrder(presentation);

  const workList = getVisibleWork(snapshot, itemVis);
  const eduList = getVisibleEducation(snapshot, itemVis);
  const skillsList = getVisibleSkills(snapshot, itemVis);
  const projectsList = getVisibleProjects(snapshot, itemVis);
  const certList = getVisibleCertificates(snapshot, itemVis);
  const awardsList = getVisibleAwards(snapshot, itemVis);
  const langList = getVisibleLanguages(snapshot, itemVis);

  const sectionTitleStyle: React.CSSProperties = {
    fontFamily: "var(--cv-font-academic, 'Palatino Linotype', 'Book Antiqua', Palatino, serif)",
    fontSize: "1.05rem",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "#1c1917",
    borderBottom: "1px solid #1c1917",
    paddingBottom: "0.2rem",
    marginBottom: "0.75rem",
    marginTop: "0.25rem",
  };

  const renderSection = (secKey: string) => {
    switch (secKey) {
      case "education":
        // In academic CVs, Education is conventionally the premier section
        if (!isSectionVisible("education", secVis, eduList.length > 0)) return null;
        return (
          <EducationSection
            key="education"
            education={eduList}
            itemVisibility={itemVis}
            title="EDUCATION & ACADEMIC APPOINTMENTS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "work":
        if (!isSectionVisible("work", secVis, workList.length > 0)) return null;
        return (
          <WorkSection
            key="work"
            work={workList}
            itemVisibility={itemVis}
            title="RESEARCH & TEACHING EXPERIENCE"
            titleStyle={sectionTitleStyle}
            showMetrics={true}
          />
        );
      case "projects":
        if (!isSectionVisible("projects", secVis, projectsList.length > 0)) return null;
        return (
          <ProjectsSection
            key="projects"
            projects={projectsList}
            itemVisibility={itemVis}
            title="PUBLICATIONS & RESEARCH PROJECTS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "awards":
        if (!isSectionVisible("awards", secVis, awardsList.length > 0)) return null;
        return (
          <AwardsSection
            key="awards"
            awards={awardsList}
            itemVisibility={itemVis}
            title="GRANTS, HONORS & FELLOWSHIPS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "certificates":
        if (!isSectionVisible("certificates", secVis, certList.length > 0)) return null;
        return (
          <CertificationsSection
            key="certificates"
            certificates={certList}
            itemVisibility={itemVis}
            title="CERTIFICATIONS & PROFESSIONAL LICENSURE"
            titleStyle={sectionTitleStyle}
          />
        );
      case "skills":
        if (!isSectionVisible("skills", secVis, skillsList.length > 0)) return null;
        return (
          <SkillsSection
            key="skills"
            skills={skillsList}
            itemVisibility={itemVis}
            title="RESEARCH METHODOLOGIES & TECHNICAL SKILLS"
            titleStyle={sectionTitleStyle}
            layout="categorized"
          />
        );
      case "languages":
        if (!isSectionVisible("languages", secVis, langList.length > 0)) return null;
        return (
          <LanguagesSection
            key="languages"
            languages={langList}
            itemVisibility={itemVis}
            title="SCHOLARLY & ANCIENT LANGUAGES"
            titleStyle={sectionTitleStyle}
          />
        );
      case "basics":
        if (!isSectionVisible("basics", secVis, !!basics?.summary || !!basics?.base_summary)) return null;
        return (
          <SummarySection
            key="summary"
            basics={basics}
            title="RESEARCH STATEMENT / ABSTRACT"
            titleStyle={sectionTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div
      className="template-academic-research"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--cv-sec-gap, 1.45rem)",
        fontFamily: "var(--cv-font-academic, 'Palatino Linotype', 'Book Antiqua', Palatino, serif)",
        color: "#1c1917",
        lineHeight: 1.5,
      }}
    >
      {/* Formal Centered Scholarly Header */}
      <div style={{ textAlign: "center", borderBottom: "1px solid #78716c", paddingBottom: "0.85rem" }}>
        <PersonalHeader basics={basics} layout="center" contactSeparator=" • " />
      </div>

      {/* Dynamic ordered sections */}
      {sectionOrder.map((secKey) => renderSection(secKey))}
    </div>
  );
}
