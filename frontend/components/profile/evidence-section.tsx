"use client";

import { useState } from "react";
import {
  Plus,
  Trash,
  PencilSimple,
  ShieldCheck,
  LinkSimple,
  FileText,
  GitBranch,
  ChartBar,
  Certificate,
  ChatText,
  Buildings,
  Folders,
  Code,
  GraduationCap,
  Trophy,
} from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, SelectField } from "@/components/ui";
import {
  useAddEvidenceAssociation,
  useCandidateProfile,
  useCreateEvidence,
  useDeleteEvidence,
  useDeleteEvidenceAssociation,
  useEvidenceList,
  useUpdateEvidence,
} from "@/hooks/use-profile";
import {
  CandidateProfileData,
  EvidenceCreatePayload,
  EvidenceItem,
  EvidenceSourceType,
  ProvenanceType,
  VerificationStatus,
} from "@/types/profile";

interface EvidenceSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const SOURCE_TYPE_LABELS: Record<EvidenceSourceType, { label: string; icon: React.ReactNode }> = {
  link: { label: "Web Link", icon: <LinkSimple size={14} aria-hidden="true" /> },
  repository: { label: "Code Repository", icon: <GitBranch size={14} aria-hidden="true" /> },
  metric_report: { label: "Metric / Performance Report", icon: <ChartBar size={14} aria-hidden="true" /> },
  document: { label: "Document / PDF", icon: <FileText size={14} aria-hidden="true" /> },
  credential: { label: "Official Credential", icon: <Certificate size={14} aria-hidden="true" /> },
  recommendation: { label: "Reference / Recommendation", icon: <ChatText size={14} aria-hidden="true" /> },
  other: { label: "Other Supporting Source", icon: <ShieldCheck size={14} aria-hidden="true" /> },
};

const VERIFICATION_TONES: Record<VerificationStatus, "green" | "blue" | "purple" | "neutral"> = {
  verified: "green",
  third_party_confirmed: "purple",
  self_attested: "blue",
  unverified: "neutral",
};

const PROVENANCE_TONES: Record<ProvenanceType, "neutral" | "blue" | "purple" | "amber"> = {
  user_provided: "neutral",
  imported: "blue",
  ai_enhanced: "purple",
  ai_generated: "amber",
};

export function EvidenceSection({ profile, onToast }: EvidenceSectionProps) {
  const { data: evidenceList = [], isLoading } = useEvidenceList();
  const createEvidenceMutation = useCreateEvidence();
  const updateEvidenceMutation = useUpdateEvidence();
  const deleteEvidenceMutation = useDeleteEvidence();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<EvidenceItem | null>(null);
  const [filterSourceType, setFilterSourceType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Form states
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [source, setSource] = useState("");
  const [sourceType, setSourceType] = useState<EvidenceSourceType>("link");
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [date, setDate] = useState("");
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus>("unverified");
  const [provenance, setProvenance] = useState<ProvenanceType>("user_provided");

  // Selected associations for new evidence
  const [selectedExperiences, setSelectedExperiences] = useState<string[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedAchievements, setSelectedAchievements] = useState<string[]>([]);
  const [selectedCertifications, setSelectedCertifications] = useState<string[]>([]);

  const handleOpenAdd = () => {
    setEditingItem(null);
    setTitle("");
    setDescription("");
    setSource("");
    setSourceType("link");
    setUrl("");
    setNotes("");
    setDate("");
    setVerificationStatus("unverified");
    setProvenance("user_provided");
    setSelectedExperiences([]);
    setSelectedProjects([]);
    setSelectedSkills([]);
    setSelectedAchievements([]);
    setSelectedCertifications([]);
    setModalOpen(true);
  };

  const handleOpenEdit = (item: EvidenceItem) => {
    setEditingItem(item);
    setTitle(item.title);
    setDescription(item.description || "");
    setSource(item.source);
    setSourceType(item.source_type || "link");
    setUrl(item.url || "");
    setNotes(item.notes || "");
    setDate(item.date || "");
    setVerificationStatus(item.verification_status || "unverified");
    setProvenance(item.provenance || "user_provided");

    // Pre-populate associations
    const expIds = item.associations.filter((a) => a.entity_type === "experience").map((a) => a.entity_id);
    const projIds = item.associations.filter((a) => a.entity_type === "project").map((a) => a.entity_id);
    const skillIds = item.associations.filter((a) => a.entity_type === "skill").map((a) => a.entity_id);
    const achIds = item.associations.filter((a) => a.entity_type === "achievement").map((a) => a.entity_id);
    const certIds = item.associations.filter((a) => a.entity_type === "certification").map((a) => a.entity_id);

    setSelectedExperiences(expIds);
    setSelectedProjects(projIds);
    setSelectedSkills(skillIds);
    setSelectedAchievements(achIds);
    setSelectedCertifications(certIds);
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      onToast("Title required", "Please enter a descriptive evidence title.", "error");
      return;
    }
    if (!source.trim()) {
      onToast("Source required", "Please enter the origin or source of the evidence.", "error");
      return;
    }

    if (url.trim() && !url.startsWith("http://") && !url.startsWith("https://")) {
      onToast("Invalid URL", "Evidence URL must start with http:// or https://", "error");
      return;
    }

    const associatedEntities = [
      ...selectedExperiences.map((id) => ({ entity_type: "experience", entity_id: id })),
      ...selectedProjects.map((id) => ({ entity_type: "project", entity_id: id })),
      ...selectedSkills.map((id) => ({ entity_type: "skill", entity_id: id })),
      ...selectedAchievements.map((id) => ({ entity_type: "achievement", entity_id: id })),
      ...selectedCertifications.map((id) => ({ entity_type: "certification", entity_id: id })),
    ];

    try {
      if (editingItem) {
        await updateEvidenceMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            title: title.trim(),
            description: description.trim() || undefined,
            source: source.trim(),
            source_type: sourceType,
            url: url.trim() || undefined,
            notes: notes.trim() || undefined,
            date: date.trim() || undefined,
            verification_status: verificationStatus,
            provenance,
          },
        });
        onToast("Evidence updated", `Saved "${title}".`, "success");
      } else {
        await createEvidenceMutation.mutateAsync({
          title: title.trim(),
          description: description.trim() || undefined,
          source: source.trim(),
          source_type: sourceType,
          url: url.trim() || undefined,
          notes: notes.trim() || undefined,
          date: date.trim() || undefined,
          verification_status: verificationStatus,
          provenance,
          associated_entities: associatedEntities,
        });
        onToast("Evidence created", `Added "${title}" to your evidence vault.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save evidence.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, evTitle: string) => {
    try {
      await deleteEvidenceMutation.mutateAsync(id);
      onToast("Evidence deleted", `Removed "${evTitle}".`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete evidence.";
      onToast("Delete failed", msg, "error");
    }
  };

  // Helper to map entity ID to human readable name
  const getEntityLabel = (type: string, id: string) => {
    if (type === "experience") {
      const exp = (profile.experiences || []).find((e) => e.id === id);
      return exp ? `${exp.company} (${exp.position})` : `Experience ${id.slice(0, 8)}`;
    }
    if (type === "project") {
      const proj = (profile.projects || []).find((p) => p.id === id);
      return proj ? proj.name : `Project ${id.slice(0, 8)}`;
    }
    if (type === "skill") {
      const skill = (profile.skills || []).find((s) => s.id === id);
      return skill ? skill.name : `Skill ${id.slice(0, 8)}`;
    }
    if (type === "achievement") {
      const ach = (profile.achievements || []).find((a) => a.id === id);
      return ach ? ach.title : `Achievement ${id.slice(0, 8)}`;
    }
    if (type === "certification") {
      const cert = (profile.certifications || []).find((c) => c.id === id);
      return cert ? cert.name : `Certification ${id.slice(0, 8)}`;
    }
    if (type === "education") {
      const edu = (profile.education || []).find((e) => e.id === id);
      return edu ? `${edu.institution} (${edu.degree})` : `Education ${id.slice(0, 8)}`;
    }
    return `${type}: ${id.slice(0, 8)}`;
  };

  const filteredList = evidenceList.filter((item) => {
    if (filterSourceType !== "all" && item.source_type !== filterSourceType) return false;
    if (filterStatus !== "all" && item.verification_status !== filterStatus) return false;
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Evidence Vault & Provenance
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            First-class factual evidence backing your career claims, experiences, projects, and skills.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Evidence
        </Button>
      </div>

      {/* Filter Tabs */}
      {evidenceList.length > 0 && (
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          <button
            type="button"
            className={filterSourceType === "all" ? "badge badge-blue" : "badge badge-neutral"}
            style={{ cursor: "pointer", fontSize: "0.8125rem", padding: "0.35rem 0.75rem" }}
            onClick={() => setFilterSourceType("all")}
          >
            All Types ({evidenceList.length})
          </button>
          {Object.entries(SOURCE_TYPE_LABELS).map(([key, config]) => {
            const count = evidenceList.filter((e) => e.source_type === key).length;
            if (count === 0) return null;
            return (
              <button
                key={key}
                type="button"
                className={filterSourceType === key ? "badge badge-blue" : "badge badge-neutral"}
                style={{ cursor: "pointer", fontSize: "0.8125rem", padding: "0.35rem 0.75rem" }}
                onClick={() => setFilterSourceType(key)}
              >
                {config.label} ({count})
              </button>
            );
          })}
        </div>
      )}

      {filteredList.length > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 22rem), 1fr))",
            gap: "1.25rem",
          }}
        >
          {filteredList.map((item) => {
            const typeConfig = SOURCE_TYPE_LABELS[item.source_type] || SOURCE_TYPE_LABELS.other;
            return (
              <Card
                key={item.id}
                style={{
                  padding: "1.25rem",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "1rem",
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                      <span
                        style={{
                          padding: "0.35rem",
                          borderRadius: "0.375rem",
                          backgroundColor: "#f1f5f9",
                          color: "#0f172a",
                          display: "inline-flex",
                        }}
                      >
                        {typeConfig.icon}
                      </span>
                      <div>
                        <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "#09090b" }}>
                          {item.title}
                        </h3>
                        <p style={{ fontSize: "0.75rem", color: "#64748b" }}>
                          Source: <strong>{item.source}</strong> {item.date ? `• ${item.date}` : ""}
                        </p>
                      </div>
                    </div>
                    <Badge tone={VERIFICATION_TONES[item.verification_status] || "neutral"}>
                      <span style={{ textTransform: "capitalize" }}>
                        {item.verification_status.replace(/_/g, " ")}
                      </span>
                    </Badge>
                  </div>

                  {item.description && (
                    <p style={{ fontSize: "0.8125rem", color: "#334155", marginTop: "0.625rem", lineHeight: "1.5" }}>
                      {item.description}
                    </p>
                  )}

                  {item.url && (
                    <div style={{ marginTop: "0.5rem" }}>
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noreferrer noopener"
                        style={{
                          fontSize: "0.75rem",
                          color: "#2563eb",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: "0.25rem",
                          wordBreak: "break-all",
                        }}
                      >
                        <LinkSimple size={13} aria-hidden="true" />
                        {item.url}
                      </a>
                    </div>
                  )}

                  {/* Provenance and Verification details */}
                  <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
                    <Badge tone={PROVENANCE_TONES[item.provenance] || "neutral"}>
                      Origin: {item.provenance.replace(/_/g, " ")}
                    </Badge>
                  </div>

                  {/* Associated profile claims */}
                  {item.associations && item.associations.length > 0 && (
                    <div style={{ marginTop: "0.875rem", borderTop: "1px dashed #e2e8f0", paddingTop: "0.625rem" }}>
                      <p style={{ fontSize: "0.6875rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                        Supports {item.associations.length} Profile Claim{item.associations.length > 1 ? "s" : ""}:
                      </p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem" }}>
                        {item.associations.map((assoc) => (
                          <span
                            key={assoc.id}
                            style={{
                              fontSize: "0.6875rem",
                              backgroundColor: "#f8fafc",
                              color: "#334155",
                              padding: "0.2rem 0.5rem",
                              borderRadius: "0.375rem",
                              border: "1px solid #e2e8f0",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                            }}
                          >
                            {assoc.entity_type === "experience" && <Buildings size={12} />}
                            {assoc.entity_type === "project" && <Folders size={12} />}
                            {assoc.entity_type === "skill" && <Code size={12} />}
                            {assoc.entity_type === "achievement" && <Trophy size={12} />}
                            {assoc.entity_type === "certification" && <Certificate size={12} />}
                            {assoc.entity_type === "education" && <GraduationCap size={12} />}
                            {getEntityLabel(assoc.entity_type, assoc.entity_id)}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    borderTop: "1px solid #f1f5f9",
                    paddingTop: "0.625rem",
                    marginTop: "0.25rem",
                  }}
                >
                  <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
                    ID: {item.id.slice(0, 8)}
                  </span>
                  <div style={{ display: "flex", gap: "0.25rem" }}>
                    <IconButton
                      label={`Edit ${item.title}`}
                      onClick={() => handleOpenEdit(item)}
                    >
                      <PencilSimple size={15} aria-hidden="true" />
                    </IconButton>
                    <IconButton
                      label={`Delete ${item.title}`}
                      onClick={() => handleDelete(item.id, item.title)}
                    >
                      <Trash size={15} aria-hidden="true" />
                    </IconButton>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card
          style={{
            padding: "3rem 1.5rem",
            textAlign: "center",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "0.75rem",
          }}
        >
          <ShieldCheck size={36} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No evidence records found
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b", maxWidth: "28rem", margin: "0 auto" }}>
              Add metrics reports, GitHub repositories, customer testimonials, or verified credentials to boost your profile quality and evidence coverage.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Evidence Record
          </Button>
        </Card>
      )}

      {/* Add / Edit Evidence Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Evidence Record" : "Add Evidence Record"}
        description="Factual artifacts and sources supporting claims in your master profile."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={createEvidenceMutation.isPending || updateEvidenceMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Create Evidence"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Field
            label="Evidence Title *"
            name="evidence_title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Distributed Queue Throughput Benchmark & Grafana Dashboards"
            required
          />

          <div className="profile-form-grid">
            <Field
              label="Source / Origin *"
              name="evidence_source"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              placeholder="e.g. Grafana / Datadog, GitHub, AWS Console"
              required
            />

            <SelectField
              label="Source Type"
              name="source_type"
              value={sourceType}
              onChange={(e) => setSourceType(e.target.value as EvidenceSourceType)}
            >
              <option value="link">Web Link</option>
              <option value="repository">Code Repository</option>
              <option value="metric_report">Metric / Performance Report</option>
              <option value="document">Document / PDF</option>
              <option value="credential">Official Credential</option>
              <option value="recommendation">Reference / Recommendation</option>
              <option value="other">Other</option>
            </SelectField>

            <SelectField
              label="Verification Status"
              name="verification_status"
              value={verificationStatus}
              onChange={(e) => setVerificationStatus(e.target.value as VerificationStatus)}
            >
              <option value="unverified">Unverified</option>
              <option value="self_attested">Self Attested</option>
              <option value="verified">Verified</option>
              <option value="third_party_confirmed">Third-Party Confirmed</option>
            </SelectField>

            <SelectField
              label="Provenance (Origin)"
              name="provenance"
              value={provenance}
              onChange={(e) => setProvenance(e.target.value as ProvenanceType)}
            >
              <option value="user_provided">User Provided</option>
              <option value="imported">Imported</option>
              <option value="ai_enhanced">AI Enhanced</option>
              <option value="ai_generated">AI Generated</option>
            </SelectField>
          </div>

          <Field
            label="URL / Link (Optional)"
            name="evidence_url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/yourname/repo or https://metrics.internal/dash"
          />

          <div className="profile-form-grid">
            <Field
              label="Date / Context"
              name="evidence_date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              placeholder="e.g. 2024-Q3 or 2023-11"
            />
            <Field
              label="Internal Verification Notes"
              name="evidence_notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. Reviewed during annual performance evaluation"
            />
          </div>

          <div className="form-group">
            <label className="field-label">Description / Factual Claim Context</label>
            <textarea
              className="input"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Explain the factual claim this evidence validates (e.g., Reduced p99 latency by 45% on edge nodes)..."
            />
          </div>

          {/* Association Checkboxes */}
          {!editingItem && (
            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.875rem" }}>
              <label className="field-label" style={{ display: "block", marginBottom: "0.5rem" }}>
                Connect to Profile Claims (Optional)
              </label>

              {/* Experiences */}
              {(profile.experiences || []).length > 0 && (
                <div style={{ marginBottom: "0.75rem" }}>
                  <p style={{ fontSize: "0.75rem", fontWeight: 600, color: "#475569", marginBottom: "0.25rem" }}>
                    Work Experience:
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                    {(profile.experiences || []).map((exp) => (
                      <label key={exp.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "#334155", cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={selectedExperiences.includes(exp.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedExperiences([...selectedExperiences, exp.id]);
                            } else {
                              setSelectedExperiences(selectedExperiences.filter((id) => id !== exp.id));
                            }
                          }}
                        />
                        <span>{exp.company} — {exp.position}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Projects */}
              {(profile.projects || []).length > 0 && (
                <div style={{ marginBottom: "0.75rem" }}>
                  <p style={{ fontSize: "0.75rem", fontWeight: 600, color: "#475569", marginBottom: "0.25rem" }}>
                    Projects:
                  </p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                    {(profile.projects || []).map((proj) => (
                      <label key={proj.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "#334155", cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={selectedProjects.includes(proj.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedProjects([...selectedProjects, proj.id]);
                            } else {
                              setSelectedProjects(selectedProjects.filter((id) => id !== proj.id));
                            }
                          }}
                        />
                        <span>{proj.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {(profile.skills || []).length > 0 && (
                <div>
                  <p style={{ fontSize: "0.75rem", fontWeight: 600, color: "#475569", marginBottom: "0.25rem" }}>
                    Skills:
                  </p>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(8rem, 1fr))", gap: "0.25rem" }}>
                    {(profile.skills || []).map((skill) => (
                      <label key={skill.id} style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8125rem", color: "#334155", cursor: "pointer" }}>
                        <input
                          type="checkbox"
                          checked={selectedSkills.includes(skill.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedSkills([...selectedSkills, skill.id]);
                            } else {
                              setSelectedSkills(selectedSkills.filter((id) => id !== skill.id));
                            }
                          }}
                        />
                        <span>{skill.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
