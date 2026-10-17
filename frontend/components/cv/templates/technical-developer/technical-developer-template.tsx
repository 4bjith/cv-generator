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

export function TechnicalDeveloperTemplate({ snapshot, presentation }: CVTemplateProps) {
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
    fontFamily: "var(--cv-font-mono, monospace)",
    fontSize: "0.92rem",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
    color: "var(--cv-accent, #0284c7)",
    borderBottom: "1.5px solid var(--cv-border, #e2e8f0)",
    paddingBottom: "0.25rem",
    marginBottom: "0.75rem",
    display: "flex",
    alignItems: "center",
    gap: "0.4rem",
  };

  const renderSection = (secKey: string) => {
    switch (secKey) {
      case "skills":
        // For technical candidates, skills is usually top priority
        if (!isSectionVisible("skills", secVis, skillsList.length > 0)) return null;
        return (
          <SkillsSection
            key="skills"
            skills={skillsList}
            itemVisibility={itemVis}
            title="// TECHNICAL SKILLS & STACK"
            titleStyle={sectionTitleStyle}
            layout="categorized"
          />
        );
      case "work":
        if (!isSectionVisible("work", secVis, workList.length > 0)) return null;
        return (
          <WorkSection
            key="work"
            work={workList}
            itemVisibility={itemVis}
            title="// ENGINEERING EXPERIENCE"
            titleStyle={sectionTitleStyle}
            showMetrics={true}
            showTech={true}
          />
        );
      case "projects":
        if (!isSectionVisible("projects", secVis, projectsList.length > 0)) return null;
        return (
          <ProjectsSection
            key="projects"
            projects={projectsList}
            itemVisibility={itemVis}
            title="// SYSTEMS & OPEN SOURCE PROJECTS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "education":
        if (!isSectionVisible("education", secVis, eduList.length > 0)) return null;
        return (
          <EducationSection
            key="education"
            education={eduList}
            itemVisibility={itemVis}
            title="// EDUCATION"
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
            title="// CERTIFICATIONS & ACCREDITATIONS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "basics":
        if (!isSectionVisible("basics", secVis, !!basics?.summary || !!basics?.base_summary)) return null;
        return (
          <SummarySection
            key="summary"
            basics={basics}
            title="// OVERVIEW"
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
            title="// HONORS & HACKATHONS"
            titleStyle={sectionTitleStyle}
          />
        );
      case "languages":
        if (!isSectionVisible("languages", secVis, langList.length > 0)) return null;
        return (
          <LanguagesSection
            key="languages"
            languages={langList}
            itemVisibility={itemVis}
            title="// LANGUAGES"
            titleStyle={sectionTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div
      className="template-technical-developer"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--cv-sec-gap, 1.3rem)",
      }}
    >
      {/* Technical Header with terminal / code vibe */}
      <div style={{ borderLeft: "4px solid var(--cv-accent, #0284c7)", paddingLeft: "1rem" }}>
        <PersonalHeader basics={basics} layout="left" contactSeparator=" // " />
      </div>

      {/* Dynamic ordered sections */}
      {sectionOrder.map((secKey) => renderSection(secKey))}
    </div>
  );
}
