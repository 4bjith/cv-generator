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

export function AtsMinimalTemplate({ snapshot, presentation }: CVTemplateProps) {
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

  // ATS-friendly standard uppercase heading with simple solid line
  const sectionTitleStyle: React.CSSProperties = {
    fontFamily: "Arial, Helvetica, sans-serif",
    fontSize: "0.98rem",
    fontWeight: "bold",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    color: "#000000",
    borderBottom: "1px solid #000000",
    paddingBottom: "2px",
    marginBottom: "0.5rem",
  };

  const renderSection = (secKey: string) => {
    switch (secKey) {
      case "basics":
        if (!isSectionVisible("basics", secVis, !!basics?.summary || !!basics?.base_summary)) return null;
        return (
          <SummarySection
            key="summary"
            basics={basics}
            title="PROFESSIONAL SUMMARY"
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
            title="WORK EXPERIENCE"
            titleStyle={sectionTitleStyle}
            showMetrics={false}
            showTech={false}
          />
        );
      case "skills":
        if (!isSectionVisible("skills", secVis, skillsList.length > 0)) return null;
        return (
          <SkillsSection
            key="skills"
            skills={skillsList}
            itemVisibility={itemVis}
            title="SKILLS"
            titleStyle={sectionTitleStyle}
            layout="categorized"
          />
        );
      case "education":
        if (!isSectionVisible("education", secVis, eduList.length > 0)) return null;
        return (
          <EducationSection
            key="education"
            education={eduList}
            itemVisibility={itemVis}
            title="EDUCATION"
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
            title="PROJECTS"
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
            title="CERTIFICATIONS"
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
            title="HONORS & AWARDS"
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
            title="LANGUAGES"
            titleStyle={sectionTitleStyle}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div
      className="template-ats-minimal"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
        fontFamily: "Arial, Helvetica, sans-serif",
        color: "#000000",
        lineHeight: 1.4,
      }}
    >
      {/* Strict linear header */}
      <PersonalHeader basics={basics} layout="left" contactSeparator=" | " avatarSize={0} />

      {/* Strictly linear single-column body */}
      {sectionOrder.map((secKey) => renderSection(secKey))}
    </div>
  );
}
