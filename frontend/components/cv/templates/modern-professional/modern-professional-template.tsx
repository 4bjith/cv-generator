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

export function ModernProfessionalTemplate({ snapshot, presentation }: CVTemplateProps) {
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
    fontSize: "0.95rem",
    fontWeight: 700,
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "var(--cv-heading, #0f172a)",
    borderBottom: "2px solid var(--cv-accent, #2563eb)",
    paddingBottom: "0.25rem",
    marginBottom: "0.75rem",
  };

  const renderSection = (secKey: string) => {
    switch (secKey) {
      case "basics":
        if (!isSectionVisible("basics", secVis, !!basics?.summary || !!basics?.base_summary)) return null;
        return (
          <SummarySection
            key="summary"
            basics={basics}
            title="Professional Summary"
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
            title="Professional Experience"
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
            title="Core Competencies & Skills"
            titleStyle={sectionTitleStyle}
            layout="categorized"
          />
        );
      case "projects":
        if (!isSectionVisible("projects", secVis, projectsList.length > 0)) return null;
        return (
          <ProjectsSection
            key="projects"
            projects={projectsList}
            itemVisibility={itemVis}
            title="Featured Projects"
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
            title="Education"
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
            title="Certifications"
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
            title="Honors & Achievements"
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
            title="Languages"
            titleStyle={sectionTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="template-modern-professional" style={{ display: "flex", flexDirection: "column", gap: "var(--cv-sec-gap, 1.35rem)" }}>
      {/* Header is always primary on top */}
      <PersonalHeader basics={basics} layout="left" contactSeparator=" • " />

      {/* Dynamic ordered sections */}
      {sectionOrder.map((secKey) => renderSection(secKey))}
    </div>
  );
}
