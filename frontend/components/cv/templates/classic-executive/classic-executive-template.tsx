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

export function ClassicExecutiveTemplate({ snapshot, presentation }: CVTemplateProps) {
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
    fontFamily: "var(--cv-font-serif, Georgia, serif)",
    fontSize: "1.08rem",
    fontWeight: 700,
    letterSpacing: "0.02em",
    color: "var(--cv-heading, #1e293b)",
    borderBottom: "1px solid var(--cv-heading, #1e293b)",
    paddingBottom: "0.2rem",
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
            title="Executive Profile"
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
            title="Leadership & Career History"
            titleStyle={sectionTitleStyle}
            showMetrics={true}
          />
        );
      case "skills":
        if (!isSectionVisible("skills", secVis, skillsList.length > 0)) return null;
        return (
          <SkillsSection
            key="skills"
            skills={skillsList}
            itemVisibility={itemVis}
            title="Executive Competencies & Areas of Expertise"
            titleStyle={sectionTitleStyle}
            layout="categorized"
          />
        );
      case "awards":
        if (!isSectionVisible("awards", secVis, awardsList.length > 0)) return null;
        return (
          <AwardsSection
            key="awards"
            awards={awardsList}
            itemVisibility={itemVis}
            title="Key Honors & Board Appointments"
            titleStyle={sectionTitleStyle}
          />
        );
      case "projects":
        if (!isSectionVisible("projects", secVis, projectsList.length > 0)) return null;
        return (
          <ProjectsSection
            key="projects"
            projects={projectsList}
            itemVisibility={itemVis}
            title="Strategic Initiatives & Key Projects"
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
            title="Education & Credentials"
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
            title="Certifications & Licensure"
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
    <div
      className="template-classic-executive"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "var(--cv-sec-gap, 1.4rem)",
        fontFamily: "var(--cv-font-serif, Georgia, serif)",
      }}
    >
      {/* Centered dignified executive header */}
      <div style={{ borderBottom: "3px double var(--cv-heading, #1e293b)", paddingBottom: "1rem" }}>
        <PersonalHeader basics={basics} layout="center" contactSeparator=" | " />
      </div>

      {/* Dynamic ordered sections */}
      {sectionOrder.map((secKey) => renderSection(secKey))}
    </div>
  );
}
