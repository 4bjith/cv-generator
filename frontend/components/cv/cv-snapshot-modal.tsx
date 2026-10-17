"use client";

import { useState } from "react";
import { Modal, Button, Badge } from "@/components/ui";
import { CVVersion } from "@/types/cv";
import { Briefcase, GraduationCap, Code, User, Eye, ListDashes } from "@phosphor-icons/react";
import { CVRenderer } from "./templates";

interface CVSnapshotModalProps {
  open: boolean;
  onClose: () => void;
  version: CVVersion | null;
}

export function CVSnapshotModal({ open, onClose, version }: CVSnapshotModalProps) {
  if (!version) return null;

  const [activeTab, setActiveTab] = useState<"preview" | "structured">("preview");
  const { content_snapshot: snap, name, status, job_target_title, job_target_company, created_at } = version;
  const basics = snap?.basics;
  const headline = basics?.label || basics?.professional_headline;
  const summary = basics?.summary || basics?.base_summary;
  const locationStr = basics?.location
    ? [basics.location.city, basics.location.region, basics.location.countryCode].filter(Boolean).join(", ")
    : [basics?.city, basics?.state, basics?.country].filter(Boolean).join(", ");

  const workList = snap?.work || snap?.experiences || [];
  const certList = snap?.certificates || snap?.certifications || [];
  const awardsList = snap?.awards || snap?.achievements || [];
  const skillsList = snap?.skills || [];
  const projectsList = snap?.projects || [];
  const educationList = snap?.education || [];
  const languagesList = snap?.languages || [];

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={name}
      description={`Snapshot created on ${new Date(created_at).toLocaleDateString(undefined, { dateStyle: "long" })}`}
    >
      {/* View Tabs */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div style={{ display: "inline-flex", borderRadius: "6px", border: "1px solid var(--color-border)", padding: "2px", background: "var(--color-surface)" }}>
          <button
            type="button"
            onClick={() => setActiveTab("preview")}
            style={{
              padding: "0.3rem 0.65rem",
              borderRadius: "4px",
              border: "none",
              fontSize: "0.82rem",
              fontWeight: activeTab === "preview" ? 600 : 400,
              background: activeTab === "preview" ? "var(--color-primary-500)" : "transparent",
              color: activeTab === "preview" ? "#ffffff" : "var(--color-text-primary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Eye size={15} />
            Formatted CV Preview
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("structured")}
            style={{
              padding: "0.3rem 0.65rem",
              borderRadius: "4px",
              border: "none",
              fontSize: "0.82rem",
              fontWeight: activeTab === "structured" ? 600 : 400,
              background: activeTab === "structured" ? "var(--color-primary-500)" : "transparent",
              color: activeTab === "structured" ? "#ffffff" : "var(--color-text-primary)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <ListDashes size={15} />
            Structured Data
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <Badge tone={status === "ready" ? "success" : status === "archived" ? "neutral" : "blue"}>
            {status.toUpperCase()}
          </Badge>
          {snap?.schema_version && (
            <Badge tone="neutral">v{snap.schema_version}</Badge>
          )}
        </div>
      </div>

      {activeTab === "preview" ? (
        <div style={{ maxHeight: "72vh", overflowY: "auto" }}>
          {snap ? (
            <CVRenderer snapshot={snap} showToolbar={true} allowTemplateSwitching={true} />
          ) : (
            <p>No snapshot content available</p>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", maxHeight: "68vh", overflowY: "auto", paddingRight: "0.25rem" }}>
          {/* Version Metadata Banner */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center", padding: "0.75rem 1rem", background: "var(--color-surface-hover)", borderRadius: "8px" }}>
            {job_target_title && (
              <span style={{ fontSize: "0.82rem", color: "var(--color-text-secondary)" }}>
                Linked Job: <strong>{job_target_company}</strong> — {job_target_title}
              </span>
            )}
          </div>

        {/* Identity & Headline */}
        {basics && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <User size={18} weight="bold" style={{ color: "var(--color-primary-500)" }} />
              <h4 style={{ margin: 0, fontSize: "0.95rem" }}>
                {basics.name || `${basics.first_name || ""} ${basics.last_name || ""}`.trim() || "Candidate Profile"}
              </h4>
            </div>
            {headline && (
              <p style={{ margin: "0 0 0.5rem 0", color: "var(--color-text-secondary)", fontSize: "0.85rem", fontWeight: 500 }}>
                {headline}
              </p>
            )}
            {summary && (
              <p style={{ margin: 0, fontSize: "0.82rem", lineHeight: 1.5, color: "var(--color-text-primary)" }}>
                {summary}
              </p>
            )}
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", fontSize: "0.78rem", color: "var(--color-text-tertiary)", marginTop: "0.5rem" }}>
              {basics.email && <span>📧 {basics.email}</span>}
              {basics.phone && <span>📞 {basics.phone}</span>}
              {locationStr && <span>📍 {locationStr}</span>}
            </div>
          </div>
        )}

        {/* Work Experiences */}
        {workList.length > 0 && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <Briefcase size={18} weight="bold" style={{ color: "var(--color-primary-500)" }} />
              <h4 style={{ margin: 0, fontSize: "0.95rem" }}>Work Experience ({workList.length})</h4>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {workList.map((exp, idx) => {
                const bullets = exp.highlights || exp.responsibilities || [];
                const expSummary = exp.summary || exp.description;
                return (
                  <div key={exp.id || idx} style={{ borderBottom: idx < workList.length - 1 ? "1px solid var(--color-border)" : "none", paddingBottom: "0.5rem" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                      <strong style={{ fontSize: "0.88rem" }}>{exp.position}</strong>
                      <span style={{ fontSize: "0.78rem", color: "var(--color-text-tertiary)" }}>
                        {exp.startDate || exp.start_date} – {exp.is_current ? "Present" : (exp.endDate || exp.end_date || "")}
                      </span>
                    </div>
                    <div style={{ fontSize: "0.82rem", color: "var(--color-text-secondary)", marginBottom: "0.25rem" }}>
                      {exp.name || exp.company} {exp.location ? `• ${exp.location}` : ""}
                    </div>
                    {expSummary && <p style={{ fontSize: "0.8rem", margin: "0.25rem 0", color: "var(--color-text-primary)" }}>{expSummary}</p>}
                    {bullets.length > 0 && (
                      <ul style={{ margin: "0.25rem 0 0 1.25rem", padding: 0, fontSize: "0.78rem" }}>
                        {bullets.map((r, i) => <li key={i}>{r}</li>)}
                      </ul>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Skills */}
        {skillsList.length > 0 && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <Code size={18} weight="bold" style={{ color: "var(--color-primary-500)" }} />
              <h4 style={{ margin: 0, fontSize: "0.95rem" }}>Skills ({skillsList.length})</h4>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
              {skillsList.map((s, idx) => (
                <span
                  key={s.id || idx}
                  style={{
                    padding: "0.2rem 0.55rem",
                    borderRadius: "4px",
                    background: "var(--color-surface-hover)",
                    fontSize: "0.78rem",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  {s.name} {(s.level || s.proficiency) ? `(${s.level || s.proficiency})` : ""}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Projects */}
        {projectsList.length > 0 && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
              <Code size={18} weight="bold" style={{ color: "var(--color-primary-500)" }} />
              <h4 style={{ margin: 0, fontSize: "0.95rem" }}>Projects ({projectsList.length})</h4>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {projectsList.map((p, idx) => (
                <div key={p.id || idx} style={{ fontSize: "0.82rem" }}>
                  <strong>{p.name}</strong> {p.role ? `(${p.role})` : ""}
                  {p.description && <p style={{ margin: "0.2rem 0", color: "var(--color-text-secondary)" }}>{p.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education & Certifications */}
        {(educationList.length > 0 || certList.length > 0) && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
              <GraduationCap size={18} weight="bold" style={{ color: "var(--color-primary-500)" }} />
              <h4 style={{ margin: 0, fontSize: "0.95rem" }}>Education & Certifications</h4>
            </div>
            {educationList.map((edu, idx) => (
              <div key={edu.id || idx} style={{ fontSize: "0.82rem", marginBottom: "0.4rem" }}>
                <strong>{edu.area || edu.studyType ? `${edu.studyType || ""} in ${edu.area || ""}`.trim() : edu.degree}</strong> — {edu.institution} {(edu.endDate || edu.end_date) ? `(${edu.endDate || edu.end_date})` : ""}
              </div>
            ))}
            {certList.map((cert, idx) => (
              <div key={cert.id || idx} style={{ fontSize: "0.82rem", color: "var(--color-text-secondary)" }}>
                📜 {cert.name} — {cert.issuer}
              </div>
            ))}
          </div>
        )}

        {/* Awards */}
        {awardsList.length > 0 && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem" }}>Awards & Honors ({awardsList.length})</h4>
            {awardsList.map((a, idx) => (
              <div key={a.id || idx} style={{ fontSize: "0.82rem", marginBottom: "0.25rem" }}>
                🏆 <strong>{a.title}</strong> {a.awarder ? `— ${a.awarder}` : ""}
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {languagesList.length > 0 && (
          <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", padding: "1rem" }}>
            <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem" }}>Languages ({languagesList.length})</h4>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.35rem" }}>
              {languagesList.map((l, idx) => (
                <span
                  key={l.id || idx}
                  style={{
                    padding: "0.2rem 0.55rem",
                    borderRadius: "4px",
                    background: "var(--color-surface-hover)",
                    fontSize: "0.78rem",
                    border: "1px solid var(--color-border)",
                  }}
                >
                  {l.language} {l.fluency ? `(${l.fluency})` : ""}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      )}

      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: "1.25rem" }}>
        <Button variant="secondary" onClick={onClose}>
          Close Snapshot
        </Button>
      </div>
    </Modal>
  );
}
