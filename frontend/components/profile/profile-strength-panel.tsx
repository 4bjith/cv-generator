"use client";

import { useState } from "react";
import { CheckCircle, WarningCircle, CaretDown, CaretUp, ArrowRight, ShieldCheck, Sparkle, TrendUp } from "@phosphor-icons/react";
import { Badge, Button, Card } from "@/components/ui";
import { ProfileStrength } from "@/types/profile";

interface ProfileStrengthPanelProps {
  strength?: ProfileStrength | null;
  onNavigateSection?: (tab: string) => void;
}

const SECTION_LABELS: Record<string, { label: string; tab: string }> = {
  personal_info: { label: "Personal Information & Headline", tab: "personal" },
  contact: { label: "Contact & Professional Links", tab: "personal" },
  professional_identity: { label: "Role & Career Level", tab: "identity" },
  summary: { label: "Base Professional Summary", tab: "identity" },
  experience: { label: "Work Experience & Metrics", tab: "experience" },
  skills: { label: "Core Skills & Categorization", tab: "skills" },
  projects: { label: "Projects & Technical Architecture", tab: "projects" },
  education: { label: "Formal Education", tab: "education" },
  certifications: { label: "Certifications & Credentials", tab: "certifications" },
  achievements: { label: "Honors & Achievements", tab: "achievements" },
  languages: { label: "Language Proficiencies", tab: "languages" },
  career_preferences: { label: "Career Preferences", tab: "preferences" },
};

export function ProfileStrengthPanel({
  strength,
  onNavigateSection,
}: ProfileStrengthPanelProps) {
  const [expanded, setExpanded] = useState(false);

  const completionPct = strength?.completion_percentage ?? 0;
  const quality = strength?.quality;
  const qualityScore = quality?.score ?? completionPct;
  const breakdown = strength?.sections_breakdown ?? {};
  const recommendations = quality?.recommendations || strength?.suggestions || [];

  const scoreTone = qualityScore >= 80 ? "#10b981" : qualityScore >= 50 ? "#2563eb" : "#f59e0b";

  return (
    <div className="profile-strength-container" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      <div className="profile-score-banner">
        <div
          className="profile-score-orbit"
          style={{ backgroundColor: scoreTone }}
        >
          <span>{qualityScore}</span>
          <small>/100</small>
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
            <p className="eyebrow" style={{ margin: 0 }}>Evidence-Backed Profile Quality</p>
            <Badge tone={qualityScore >= 80 ? "green" : qualityScore >= 50 ? "blue" : "amber"}>
              {qualityScore >= 80
                ? "Master-Level Evidence"
                : qualityScore >= 50
                ? "Good Quality"
                : "Foundation Needed"}
            </Badge>
          </div>
          <h2 style={{ marginTop: "0.25rem" }}>
            {qualityScore >= 80
              ? "Comprehensive & Evidence-Backed Master Profile"
              : qualityScore >= 50
              ? "Solid Profile with Evidence & Skill Link Gaps"
              : "Early Profile Setup"}
          </h2>
          <p>
            {recommendations.length > 0
              ? recommendations[0]
              : "Your master career knowledge base has complete, evidence-backed information ready for tailored applications."}
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setExpanded(!expanded)}
          icon={expanded ? <CaretUp size={15} aria-hidden="true" /> : <CaretDown size={15} aria-hidden="true" />}
        >
          {expanded ? "Hide Quality Audit" : "Review Quality Breakdown"}
        </Button>
      </div>

      {expanded && (
        <Card style={{ padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Dimensional Quality Breakdown */}
          {quality && (
            <div>
              <div className="card-heading" style={{ marginBottom: "0.875rem" }}>
                <div>
                  <p className="eyebrow">Evidence & Quality Dimensions</p>
                  <h2>Multi-Dimensional Scoring</h2>
                </div>
                <Badge tone="purple">Composite: {quality.score}/100</Badge>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 13rem), 1fr))", gap: "1rem" }}>
                {/* Completeness */}
                <div style={{ padding: "0.875rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                    <span style={{ fontWeight: 600 }}>Completeness (30%)</span>
                    <strong>{quality.completeness}%</strong>
                  </div>
                  <div style={{ height: "0.4rem", backgroundColor: "#e2e8f0", borderRadius: "0.2rem", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${quality.completeness}%`, backgroundColor: "#2563eb" }} />
                  </div>
                </div>

                {/* Evidence Coverage */}
                <div style={{ padding: "0.875rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                    <span style={{ fontWeight: 600 }}>Evidence Coverage (25%)</span>
                    <strong>{quality.evidence_coverage}%</strong>
                  </div>
                  <div style={{ height: "0.4rem", backgroundColor: "#e2e8f0", borderRadius: "0.2rem", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${quality.evidence_coverage}%`, backgroundColor: "#10b981" }} />
                  </div>
                </div>

                {/* Skill Validation */}
                <div style={{ padding: "0.875rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                    <span style={{ fontWeight: 600 }}>Skill Relational Proof (20%)</span>
                    <strong>{quality.skill_validation}%</strong>
                  </div>
                  <div style={{ height: "0.4rem", backgroundColor: "#e2e8f0", borderRadius: "0.2rem", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${quality.skill_validation}%`, backgroundColor: "#8b5cf6" }} />
                  </div>
                </div>

                {/* Experience Quality */}
                <div style={{ padding: "0.875rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                    <span style={{ fontWeight: 600 }}>Experience Depth (15%)</span>
                    <strong>{quality.experience_quality}%</strong>
                  </div>
                  <div style={{ height: "0.4rem", backgroundColor: "#e2e8f0", borderRadius: "0.2rem", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${quality.experience_quality}%`, backgroundColor: "#06b6d4" }} />
                  </div>
                </div>

                {/* Project Quality */}
                <div style={{ padding: "0.875rem", backgroundColor: "#f8fafc", borderRadius: "0.5rem", border: "1px solid #e2e8f0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#475569", marginBottom: "0.25rem" }}>
                    <span style={{ fontWeight: 600 }}>Project Architecture (10%)</span>
                    <strong>{quality.project_quality}%</strong>
                  </div>
                  <div style={{ height: "0.4rem", backgroundColor: "#e2e8f0", borderRadius: "0.2rem", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${quality.project_quality}%`, backgroundColor: "#f59e0b" }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actionable Recommendations */}
          {recommendations.length > 0 && (
            <div
              style={{
                padding: "1.125rem",
                backgroundColor: "#f0fdf4",
                borderRadius: "0.75rem",
                border: "1px solid #bbf7d0",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                <ShieldCheck size={18} className="text-emerald-700" aria-hidden="true" />
                <p style={{ fontSize: "0.8125rem", fontWeight: 700, color: "#166534", textTransform: "uppercase", margin: 0 }}>
                  High-Impact Quality Recommendations
                </p>
              </div>
              <ul style={{ listStyleType: "disc", paddingLeft: "1.25rem", fontSize: "0.8125rem", color: "#14532d", display: "flex", flexDirection: "column", gap: "0.35rem" }}>
                {recommendations.map((rec, idx) => (
                  <li key={idx} style={{ lineHeight: "1.4" }}>{rec}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Sections Checklist */}
          <div>
            <div className="card-heading" style={{ marginBottom: "0.75rem" }}>
              <div>
                <p className="eyebrow">Section Checklist</p>
                <h2>Master Profile Sections</h2>
              </div>
              <Badge tone={completionPct >= 80 ? "green" : "blue"}>
                {strength?.completed_sections_count ?? 0} of {strength?.total_sections_count ?? 12} Complete
              </Badge>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 17rem), 1fr))",
                gap: "0.75rem",
              }}
            >
              {Object.entries(SECTION_LABELS).map(([key, config]) => {
                const isComplete = Boolean(breakdown[key]);
                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => onNavigateSection?.(config.tab)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      padding: "0.75rem 1rem",
                      borderRadius: "0.75rem",
                      border: "1px solid",
                      borderColor: isComplete ? "#d1fae5" : "#e2e8f0",
                      backgroundColor: isComplete ? "#f0fdf4" : "#f8fafc",
                      textAlign: "left",
                      cursor: "pointer",
                      transition: "all 0.15s ease",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: "0.625rem" }}>
                      {isComplete ? (
                        <CheckCircle size={18} weight="fill" className="text-emerald-600" aria-hidden="true" />
                      ) : (
                        <WarningCircle size={18} weight="fill" className="text-amber-500" aria-hidden="true" />
                      )}
                      <span
                        style={{
                          fontSize: "0.8125rem",
                          fontWeight: 600,
                          color: isComplete ? "#065f46" : "#334155",
                        }}
                      >
                        {config.label}
                      </span>
                    </div>
                    <ArrowRight size={14} className="text-slate-400" aria-hidden="true" />
                  </button>
                );
              })}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
