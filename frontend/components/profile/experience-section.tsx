"use client";

import { useState } from "react";
import {
  Briefcase,
  Plus,
  Trash,
  PencilSimple,
  CheckCircle,
  TrendUp,
  X,
  ShieldCheck,
} from "@phosphor-icons/react";
import {
  Badge,
  Button,
  Card,
  Field,
  IconButton,
  Modal,
  SelectField,
  TextareaField,
} from "@/components/ui";
import {
  useAddExperience,
  useDeleteExperience,
  useUpdateExperience,
} from "@/hooks/use-profile";
import {
  CandidateProfileData,
  EmploymentType,
  ExperienceMetric,
  ProvenanceType,
  WorkExperience,
} from "@/types/profile";

interface ExperienceSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const PROVENANCE_TONES: Record<ProvenanceType, "neutral" | "blue" | "purple" | "amber"> = {
  user_provided: "neutral",
  imported: "blue",
  ai_enhanced: "purple",
  ai_generated: "amber",
};

export function ExperienceSection({ profile, onToast }: ExperienceSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<WorkExperience | null>(null);

  // Form state
  const [company, setCompany] = useState("");
  const [position, setPosition] = useState("");
  const [employmentType, setEmploymentType] = useState<EmploymentType>("full_time");
  const [location, setLocation] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [isCurrent, setIsCurrent] = useState(false);
  const [description, setDescription] = useState("");
  const [responsibilitiesText, setResponsibilitiesText] = useState("");
  const [achievementsText, setAchievementsText] = useState("");
  const [technologiesText, setTechnologiesText] = useState("");
  const [provenance, setProvenance] = useState<ProvenanceType>("user_provided");

  // Metrics Builder state
  const [metrics, setMetrics] = useState<ExperienceMetric[]>([]);
  const [metricValue, setMetricValue] = useState("");
  const [metricUnit, setMetricUnit] = useState("");
  const [metricDesc, setMetricDesc] = useState("");

  const addExperienceMutation = useAddExperience();
  const updateExperienceMutation = useUpdateExperience();
  const deleteExperienceMutation = useDeleteExperience();

  const handleOpenAdd = () => {
    setEditingItem(null);
    setCompany("");
    setPosition("");
    setEmploymentType("full_time");
    setLocation("");
    setStartDate("");
    setEndDate("");
    setIsCurrent(false);
    setDescription("");
    setResponsibilitiesText("");
    setAchievementsText("");
    setTechnologiesText("");
    setProvenance("user_provided");
    setMetrics([]);
    setMetricValue("");
    setMetricUnit("");
    setMetricDesc("");
    setModalOpen(true);
  };

  const handleOpenEdit = (item: WorkExperience) => {
    setEditingItem(item);
    setCompany(item.company);
    setPosition(item.position);
    setEmploymentType((item.employment_type as EmploymentType) || "full_time");
    setLocation(item.location || "");
    setStartDate(item.start_date);
    setEndDate(item.end_date || "");
    setIsCurrent(item.is_current);
    setDescription(item.description || "");
    setResponsibilitiesText((item.responsibilities || []).join("\n"));
    setAchievementsText((item.achievements || []).join("\n"));
    setTechnologiesText((item.technologies || []).join(", "));
    setProvenance(item.provenance || "user_provided");
    setMetrics(item.metrics || []);
    setMetricValue("");
    setMetricUnit("");
    setMetricDesc("");
    setModalOpen(true);
  };

  const handleAddMetric = (e: React.FormEvent) => {
    e.preventDefault();
    if (!metricValue.trim() || !metricUnit.trim() || !metricDesc.trim()) {
      onToast("Incomplete metric", "Please fill in metric value, unit, and description.", "error");
      return;
    }
    const val = isNaN(Number(metricValue.trim())) ? metricValue.trim() : Number(metricValue.trim());
    setMetrics([
      ...metrics,
      { value: val, unit: metricUnit.trim(), description: metricDesc.trim() },
    ]);
    setMetricValue("");
    setMetricUnit("");
    setMetricDesc("");
  };

  const handleRemoveMetric = (idx: number) => {
    setMetrics(metrics.filter((_, i) => i !== idx));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim() || !position.trim() || !startDate.trim()) {
      onToast("Missing required fields", "Company, Position, and Start Date are required.", "error");
      return;
    }

    if (!isCurrent && endDate.trim() && endDate.trim() < startDate.trim()) {
      onToast("Invalid date range", "End date cannot precede start date.", "error");
      return;
    }

    const responsibilities = responsibilitiesText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const achievements = achievementsText
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);

    const technologies = technologiesText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    try {
      if (editingItem) {
        await updateExperienceMutation.mutateAsync({
          id: editingItem.id,
          payload: {
            company: company.trim(),
            position: position.trim(),
            employment_type: employmentType,
            location: location.trim() || undefined,
            start_date: startDate.trim(),
            end_date: isCurrent ? null : endDate.trim() || null,
            is_current: isCurrent,
            description: description.trim() || undefined,
            responsibilities,
            achievements,
            technologies,
            metrics,
            provenance,
          },
        });
        onToast("Experience updated", `Saved ${company}.`, "success");
      } else {
        await addExperienceMutation.mutateAsync({
          company: company.trim(),
          position: position.trim(),
          employment_type: employmentType,
          location: location.trim() || undefined,
          start_date: startDate.trim(),
          end_date: isCurrent ? null : endDate.trim() || null,
          is_current: isCurrent,
          description: description.trim() || undefined,
          responsibilities,
          achievements,
          technologies,
          metrics,
          provenance,
          order_index: (profile.experiences?.length || 0),
        });
        onToast("Experience added", `Added ${position} at ${company}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save experience record.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, comp: string) => {
    try {
      await deleteExperienceMutation.mutateAsync(id);
      onToast("Experience deleted", `Removed experience at ${comp}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete experience.";
      onToast("Delete failed", msg, "error");
    }
  };

  return (
    <div className="experience-stack">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Work History & Evidence
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Maintain full factual records of past positions, distinct achievements, and measurable metrics backed by evidence.
          </p>
        </div>
        <Button
          icon={<Plus size={16} aria-hidden="true" />}
          onClick={handleOpenAdd}
        >
          Add Experience
        </Button>
      </div>

      {profile.experiences && profile.experiences.length > 0 ? (
        profile.experiences.map((exp) => {
          const evidenceCount = (exp.evidence_ids || []).length;
          return (
            <Card key={exp.id} className="experience-card">
              <div className="experience-header">
                <div className="experience-title">
                  <span className="experience-dot" />
                  <div>
                    <h2>{exp.position}</h2>
                    <p>
                      <strong>{exp.company}</strong>
                      {exp.location ? ` · ${exp.location}` : ""} ·{" "}
                      <span style={{ textTransform: "capitalize" }}>
                        {exp.employment_type?.replace("_", " ")}
                      </span>
                    </p>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.25rem" }}>
                    <span className="experience-date">
                      {exp.start_date} to {exp.is_current ? "Present" : exp.end_date || "—"}
                    </span>
                    {exp.provenance && (
                      <Badge tone={PROVENANCE_TONES[exp.provenance] || "neutral"}>
                        {exp.provenance.replace(/_/g, " ")}
                      </Badge>
                    )}
                  </div>
                  <IconButton
                    label={`Edit ${exp.company}`}
                    onClick={() => handleOpenEdit(exp)}
                  >
                    <PencilSimple size={16} aria-hidden="true" />
                  </IconButton>
                  <IconButton
                    label={`Delete ${exp.company}`}
                    onClick={() => handleDelete(exp.id, exp.company)}
                  >
                    <Trash size={16} aria-hidden="true" />
                  </IconButton>
                </div>
              </div>

              {exp.description && (
                <p className="experience-description">{exp.description}</p>
              )}

              {/* Responsibilities */}
              {exp.responsibilities && exp.responsibilities.length > 0 && (
                <div>
                  <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                    Key Responsibilities
                  </p>
                  <ul className="bullet-list">
                    {exp.responsibilities.map((resp, i) => (
                      <li key={i}>{resp}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Achievements */}
              {exp.achievements && exp.achievements.length > 0 && (
                <div>
                  <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#047857", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                    Verified Achievements & Outcomes
                  </p>
                  <ul className="bullet-list" style={{ color: "#065f46" }}>
                    {exp.achievements.map((ach, i) => (
                      <li key={i}>{ach}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Measurable Metrics */}
              {exp.metrics && exp.metrics.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.25rem" }}>
                  {exp.metrics.map((m, i) => (
                    <div
                      key={i}
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.5rem",
                        padding: "0.375rem 0.75rem",
                        backgroundColor: "#ecfdf5",
                        border: "1px solid #a7f3d0",
                        borderRadius: "0.5rem",
                        fontSize: "0.75rem",
                      }}
                    >
                      <TrendUp size={15} className="text-emerald-600" aria-hidden="true" />
                      <strong>
                        {m.value} {m.unit}
                      </strong>
                      <span style={{ color: "#065f46" }}>— {m.description}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Technologies */}
              {exp.technologies && exp.technologies.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem", paddingTop: "0.25rem" }}>
                  {exp.technologies.map((tech) => (
                    <Badge key={tech} tone="neutral">
                      {tech}
                    </Badge>
                  ))}
                </div>
              )}

              <div className="evidence-row">
                <CheckCircle size={15} weight="fill" aria-hidden="true" />
                <span>Evidence source: User confirmed master career fact</span>
                {evidenceCount > 0 ? (
                  <Badge tone="green">
                    <ShieldCheck size={12} style={{ display: "inline", marginRight: "0.25rem" }} />
                    {evidenceCount} Evidence Record{evidenceCount > 1 ? "s" : ""} Linked
                  </Badge>
                ) : (
                  <Badge tone="neutral">No direct evidence link</Badge>
                )}
              </div>
            </Card>
          );
        })
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
          <Briefcase size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No work experiences added
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add your current and previous professional roles with responsibilities and measurable outcomes.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Experience
          </Button>
        </Card>
      )}

      {/* Experience Modal */}
      <Modal
        open={modalOpen}
        title={editingItem ? "Edit Work Experience" : "Add Work Experience"}
        description="Provide comprehensive, evidence-backed details of this role."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addExperienceMutation.isPending || updateExperienceMutation.isPending}
            >
              {editingItem ? "Save Changes" : "Save Experience"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxHeight: "70vh", overflowY: "auto", paddingRight: "0.25rem" }}>
          <div className="profile-form-grid">
            <Field
              label="Company Name *"
              name="company"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Northstar Labs"
              required
            />
            <Field
              label="Job Position / Title *"
              name="position"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              placeholder="e.g. Staff Frontend Engineer"
              required
            />
            <SelectField
              label="Employment Type"
              name="employment_type"
              value={employmentType}
              onChange={(e) => setEmploymentType(e.target.value as EmploymentType)}
            >
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
              <option value="freelance">Freelance</option>
              <option value="temporary">Temporary</option>
              <option value="volunteer">Volunteer</option>
              <option value="other">Other</option>
            </SelectField>
            <Field
              label="Location"
              name="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. San Francisco, CA / Remote"
            />
            <Field
              label="Start Date *"
              name="start_date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="YYYY-MM (e.g. 2022-01)"
              required
            />
            <Field
              label="End Date"
              name="end_date"
              value={endDate}
              disabled={isCurrent}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder={isCurrent ? "Present" : "YYYY-MM (e.g. 2024-06)"}
            />
            <SelectField
              label="Provenance (Origin)"
              name="experience_provenance"
              value={provenance}
              onChange={(e) => setProvenance(e.target.value as ProvenanceType)}
            >
              <option value="user_provided">User Provided</option>
              <option value="imported">Imported</option>
              <option value="ai_enhanced">AI Enhanced</option>
              <option value="ai_generated">AI Generated</option>
            </SelectField>
          </div>

          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={isCurrent}
              onChange={(e) => setIsCurrent(e.target.checked)}
            />
            <span>I currently work in this role</span>
          </label>

          <TextareaField
            label="Role Overview / Description"
            name="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="High-level description of team scope, domain context, and product impact..."
            rows={3}
          />

          <TextareaField
            label="Responsibilities (one per line)"
            name="responsibilities"
            value={responsibilitiesText}
            onChange={(e) => setResponsibilitiesText(e.target.value)}
            placeholder="Architected token-driven design systems&#10;Led sprint planning for 6 engineers&#10;Maintained high-scale web platform"
            rows={4}
            hint="Keep responsibilities separate from measurable achievements."
          />

          <TextareaField
            label="Achievements & Outcomes (one per line)"
            name="achievements"
            value={achievementsText}
            onChange={(e) => setAchievementsText(e.target.value)}
            placeholder="Reduced initial bundle size by 42%&#10;Delivered real-time collaboration canvas 2 weeks ahead of schedule"
            rows={4}
            hint="List concrete results and accomplishments."
          />

          {/* Metrics Builder */}
          <div style={{ padding: "1rem", backgroundColor: "#f8fafc", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
            <p style={{ fontSize: "0.8125rem", fontWeight: 700, color: "#09090b", marginBottom: "0.5rem" }}>
              Structured Metrics & Evidence (Optional)
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 2fr auto", gap: "0.5rem", alignItems: "end" }}>
              <input
                className="input"
                placeholder="Value (e.g. 35)"
                value={metricValue}
                onChange={(e) => setMetricValue(e.target.value)}
              />
              <input
                className="input"
                placeholder="Unit (e.g. % or ms)"
                value={metricUnit}
                onChange={(e) => setMetricUnit(e.target.value)}
              />
              <input
                className="input"
                placeholder="Description (e.g. API latency reduction)"
                value={metricDesc}
                onChange={(e) => setMetricDesc(e.target.value)}
              />
              <Button size="sm" variant="secondary" onClick={handleAddMetric}>
                Add Metric
              </Button>
            </div>

            {metrics.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.75rem" }}>
                {metrics.map((m, idx) => (
                  <Badge key={idx} tone="green">
                    <strong>
                      {m.value} {m.unit}
                    </strong>
                    : {m.description}
                    <button
                      type="button"
                      onClick={() => handleRemoveMetric(idx)}
                      style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                      aria-label="Remove metric"
                    >
                      <X size={12} aria-hidden="true" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}
          </div>

          <Field
            label="Technologies & Tools Used (comma-separated)"
            name="technologies"
            value={technologiesText}
            onChange={(e) => setTechnologiesText(e.target.value)}
            placeholder="React, TypeScript, GraphQL, Tailwind CSS, Redis"
          />
        </form>
      </Modal>
    </div>
  );
}
