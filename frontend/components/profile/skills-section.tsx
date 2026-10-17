"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, Code, SealCheck, X, Buildings, Folders } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, SelectField } from "@/components/ui";
import {
  useAddSkill,
  useDeleteSkill,
  useSyncSkillRelationships,
  useUpdateSkill,
} from "@/hooks/use-profile";
import {
  CandidateProfileData,
  CandidateSkill,
  ProvenanceType,
  SkillCategory,
  SkillProficiency,
} from "@/types/profile";

interface SkillsSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const CATEGORY_NAMES: Record<string, string> = {
  programming_language: "Programming Languages",
  frontend: "Frontend Engineering",
  backend: "Backend & Systems",
  database: "Databases & Storage",
  framework: "Frameworks",
  library: "Libraries",
  cloud: "Cloud & Infrastructure",
  devops: "DevOps & CI/CD",
  testing: "Testing & QA",
  ai_ml: "AI & Machine Learning",
  design: "UI/UX & Design",
  tool: "Developer Tools",
  soft_skill: "Leadership & Collaboration",
  domain: "Industry Domain Knowledge",
  other: "Other Competencies",
};

const PROFICIENCY_TONES: Record<string, "neutral" | "blue" | "purple" | "green"> = {
  beginner: "neutral",
  intermediate: "blue",
  advanced: "purple",
  expert: "green",
};

const PROVENANCE_TONES: Record<ProvenanceType, "neutral" | "blue" | "purple" | "amber"> = {
  user_provided: "neutral",
  imported: "blue",
  ai_enhanced: "purple",
  ai_generated: "amber",
};

export function SkillsSection({ profile, onToast }: SkillsSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<CandidateSkill | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>("all");

  // Form state
  const [name, setName] = useState("");
  const [category, setCategory] = useState<SkillCategory>("frontend");
  const [proficiency, setProficiency] = useState<SkillProficiency>("advanced");
  const [yearsExperience, setYearsExperience] = useState("");
  const [lastUsed, setLastUsed] = useState("");
  const [provenance, setProvenance] = useState<ProvenanceType>("user_provided");
  const [evidenceRefs, setEvidenceRefs] = useState<string[]>([]);
  const [newRef, setNewRef] = useState("");

  // Relationships state
  const [selectedExpIds, setSelectedExpIds] = useState<string[]>([]);
  const [selectedProjIds, setSelectedProjIds] = useState<string[]>([]);

  const addSkillMutation = useAddSkill();
  const updateSkillMutation = useUpdateSkill();
  const syncRelationshipsMutation = useSyncSkillRelationships();
  const deleteSkillMutation = useDeleteSkill();

  const handleOpenAdd = () => {
    setEditingSkill(null);
    setName("");
    setCategory("frontend");
    setProficiency("advanced");
    setYearsExperience("");
    setLastUsed(new Date().getFullYear().toString());
    setProvenance("user_provided");
    setEvidenceRefs([]);
    setNewRef("");
    setSelectedExpIds([]);
    setSelectedProjIds([]);
    setModalOpen(true);
  };

  const handleOpenEdit = (skill: CandidateSkill) => {
    setEditingSkill(skill);
    setName(skill.name);
    setCategory((skill.category as SkillCategory) || "frontend");
    setProficiency((skill.proficiency as SkillProficiency) || "intermediate");
    setYearsExperience(skill.years_of_experience?.toString() || "");
    setLastUsed(skill.last_used || "");
    setProvenance(skill.provenance || "user_provided");
    setEvidenceRefs(skill.evidence_references || []);
    setNewRef("");
    setSelectedExpIds(skill.experience_ids || []);
    setSelectedProjIds(skill.project_ids || []);
    setModalOpen(true);
  };

  const handleAddRef = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRef.trim()) return;
    if (!evidenceRefs.includes(newRef.trim())) {
      setEvidenceRefs([...evidenceRefs, newRef.trim()]);
    }
    setNewRef("");
  };

  const handleRemoveRef = (ref: string) => {
    setEvidenceRefs(evidenceRefs.filter((r) => r !== ref));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      onToast("Skill name required", "Please enter a skill name.", "error");
      return;
    }

    const parsedYears = yearsExperience.trim() ? parseFloat(yearsExperience) : undefined;

    try {
      if (editingSkill) {
        await updateSkillMutation.mutateAsync({
          id: editingSkill.id,
          payload: {
            name: name.trim(),
            category,
            proficiency,
            years_of_experience: parsedYears,
            last_used: lastUsed.trim() || undefined,
            evidence_references: evidenceRefs,
            provenance,
            experience_ids: selectedExpIds,
            project_ids: selectedProjIds,
          },
        });

        // Sync explicit relationships
        await syncRelationshipsMutation.mutateAsync({
          skillId: editingSkill.id,
          payload: {
            experience_ids: selectedExpIds,
            project_ids: selectedProjIds,
          },
        });

        onToast("Skill updated", `Saved ${name}.`, "success");
      } else {
        await addSkillMutation.mutateAsync({
          name: name.trim(),
          category,
          proficiency,
          years_of_experience: parsedYears,
          last_used: lastUsed.trim() || undefined,
          evidence_references: evidenceRefs,
          provenance,
          experience_ids: selectedExpIds,
          project_ids: selectedProjIds,
        });
        onToast("Skill added", `Added ${name}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save skill.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, skillName: string) => {
    try {
      await deleteSkillMutation.mutateAsync(id);
      onToast("Skill deleted", `Removed ${skillName}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete skill.";
      onToast("Delete failed", msg, "error");
    }
  };

  const skillsList = profile.skills || [];
  const filteredSkills =
    filterCategory === "all"
      ? skillsList
      : skillsList.filter((s) => s.category === filterCategory);

  const categoriesPresent = Array.from(new Set(skillsList.map((s) => s.category || "other")));

  // Helpers for mapping linked IDs to names
  const experiencesMap = new Map((profile.experiences || []).map((e) => [e.id, `${e.company}`]));
  const projectsMap = new Map((profile.projects || []).map((p) => [p.id, p.name]));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            Skills & Evidence Map
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Rich skill profiles with categories, proficiency, years of experience, and explicit relationships to work history and projects.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Skill
        </Button>
      </div>

      {/* Category filter tabs */}
      {skillsList.length > 0 && (
        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", borderBottom: "1px solid #e2e8f0", paddingBottom: "0.5rem" }}>
          <button
            type="button"
            className={filterCategory === "all" ? "badge badge-blue" : "badge badge-neutral"}
            style={{ cursor: "pointer", fontSize: "0.8125rem", padding: "0.35rem 0.75rem" }}
            onClick={() => setFilterCategory("all")}
          >
            All Skills ({skillsList.length})
          </button>
          {categoriesPresent.map((cat) => (
            <button
              key={cat}
              type="button"
              className={filterCategory === cat ? "badge badge-blue" : "badge badge-neutral"}
              style={{ cursor: "pointer", fontSize: "0.8125rem", padding: "0.35rem 0.75rem" }}
              onClick={() => setFilterCategory(cat)}
            >
              {CATEGORY_NAMES[cat] || cat} ({skillsList.filter((s) => (s.category || "other") === cat).length})
            </button>
          ))}
        </div>
      )}

      {filteredSkills.length > 0 ? (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 19.5rem), 1fr))",
            gap: "1rem",
          }}
        >
          {filteredSkills.map((skill) => {
            const linkedExpCount = (skill.experience_ids || []).length;
            const linkedProjCount = (skill.project_ids || []).length;
            const hasRelationships = linkedExpCount > 0 || linkedProjCount > 0;

            return (
              <Card
                key={skill.id}
                style={{
                  padding: "1.25rem",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "space-between",
                  gap: "0.875rem",
                }}
              >
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem" }}>
                    <div>
                      <h3 style={{ fontSize: "1.0625rem", fontWeight: 700, color: "#09090b" }}>
                        {skill.name}
                      </h3>
                      <p style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "capitalize", marginTop: "0.125rem" }}>
                        {CATEGORY_NAMES[skill.category || "other"] || skill.category}
                      </p>
                    </div>
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.25rem" }}>
                      <Badge tone={PROFICIENCY_TONES[skill.proficiency || "intermediate"] || "neutral"}>
                        <span style={{ textTransform: "capitalize" }}>{skill.proficiency || "Competent"}</span>
                      </Badge>
                      {skill.provenance && (
                        <Badge tone={PROVENANCE_TONES[skill.provenance] || "neutral"}>
                          {skill.provenance.replace(/_/g, " ")}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: "1rem", fontSize: "0.75rem", color: "#475569", marginTop: "0.625rem" }}>
                    {skill.years_of_experience != null && (
                      <span>
                        <strong>{skill.years_of_experience}</strong> yrs experience
                      </span>
                    )}
                    {skill.last_used && (
                      <span>
                        Last used: <strong>{skill.last_used}</strong>
                      </span>
                    )}
                  </div>

                  {/* Explicit Relationships ("Used in") */}
                  {hasRelationships && (
                    <div style={{ marginTop: "0.75rem", borderTop: "1px dashed #e2e8f0", paddingTop: "0.5rem" }}>
                      <p style={{ fontSize: "0.6875rem", fontWeight: 700, color: "#64748b", textTransform: "uppercase", marginBottom: "0.375rem" }}>
                        Applied In:
                      </p>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem" }}>
                        {(skill.experience_ids || []).map((expId) => (
                          <span
                            key={expId}
                            style={{
                              fontSize: "0.6875rem",
                              backgroundColor: "#f0fdf4",
                              color: "#166534",
                              padding: "0.15rem 0.5rem",
                              borderRadius: "0.375rem",
                              border: "1px solid #bbf7d0",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                            }}
                          >
                            <Buildings size={12} />
                            {experiencesMap.get(expId) || "Experience"}
                          </span>
                        ))}
                        {(skill.project_ids || []).map((projId) => (
                          <span
                            key={projId}
                            style={{
                              fontSize: "0.6875rem",
                              backgroundColor: "#eff6ff",
                              color: "#1e40af",
                              padding: "0.15rem 0.5rem",
                              borderRadius: "0.375rem",
                              border: "1px solid #bfdbfe",
                              display: "inline-flex",
                              alignItems: "center",
                              gap: "0.25rem",
                            }}
                          >
                            <Folders size={12} />
                            {projectsMap.get(projId) || "Project"}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {skill.evidence_references && skill.evidence_references.length > 0 && (
                    <div style={{ marginTop: "0.625rem", display: "flex", flexWrap: "wrap", gap: "0.375rem" }}>
                      {skill.evidence_references.map((ref, idx) => (
                        <span
                          key={idx}
                          style={{
                            fontSize: "0.6875rem",
                            backgroundColor: "#f1f5f9",
                            color: "#334155",
                            padding: "0.15rem 0.5rem",
                            borderRadius: "0.375rem",
                            border: "1px solid #e2e8f0",
                          }}
                        >
                          ✓ {ref}
                        </span>
                      ))}
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
                  <span style={{ fontSize: "0.75rem", color: hasRelationships ? "#10b981" : "#64748b", display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                    <SealCheck size={14} weight="fill" aria-hidden="true" />
                    {hasRelationships ? "Factual Backing" : "Unlinked Skill"}
                  </span>
                  <div style={{ display: "flex", gap: "0.25rem" }}>
                    <IconButton
                      label={`Edit ${skill.name}`}
                      onClick={() => handleOpenEdit(skill)}
                    >
                      <PencilSimple size={15} aria-hidden="true" />
                    </IconButton>
                    <IconButton
                      label={`Delete ${skill.name}`}
                      onClick={() => handleDelete(skill.id, skill.name)}
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
          <Code size={32} className="text-slate-400" aria-hidden="true" />
          <div>
            <h3 style={{ fontSize: "1.125rem", fontWeight: 600, color: "#09090b" }}>
              No skills found
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add at least 3 core technical or domain skills to complete your profile foundation.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Skill
          </Button>
        </Card>
      )}

      {/* Skill Modal */}
      <Modal
        open={modalOpen}
        title={editingSkill ? "Edit Skill" : "Add Skill"}
        description="Add a verified skill and explicitly link it to your work experiences and projects."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addSkillMutation.isPending || updateSkillMutation.isPending || syncRelationshipsMutation.isPending}
            >
              {editingSkill ? "Save Changes" : "Add Skill"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <Field
            label="Skill Name *"
            name="skill_name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. TypeScript, React, PostgreSQL"
            required
          />
          <div className="profile-form-grid">
            <SelectField
              label="Category"
              name="skill_category"
              value={category}
              onChange={(e) => setCategory(e.target.value as SkillCategory)}
            >
              <option value="programming_language">Programming Language</option>
              <option value="frontend">Frontend</option>
              <option value="backend">Backend</option>
              <option value="database">Database</option>
              <option value="framework">Framework</option>
              <option value="library">Library</option>
              <option value="cloud">Cloud</option>
              <option value="devops">DevOps</option>
              <option value="testing">Testing</option>
              <option value="ai_ml">AI & ML</option>
              <option value="design">Design</option>
              <option value="tool">Tool</option>
              <option value="soft_skill">Soft Skill</option>
              <option value="domain">Domain</option>
              <option value="other">Other</option>
            </SelectField>

            <SelectField
              label="Proficiency Level"
              name="skill_proficiency"
              value={proficiency}
              onChange={(e) => setProficiency(e.target.value as SkillProficiency)}
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
              <option value="expert">Expert</option>
            </SelectField>

            <Field
              label="Years of Experience"
              name="years_experience"
              type="number"
              step="0.5"
              min="0"
              value={yearsExperience}
              onChange={(e) => setYearsExperience(e.target.value)}
              placeholder="e.g. 4.5"
            />

            <Field
              label="Last Used (Year)"
              name="last_used"
              value={lastUsed}
              onChange={(e) => setLastUsed(e.target.value)}
              placeholder="e.g. 2026"
            />

            <SelectField
              label="Provenance (Origin)"
              name="skill_provenance"
              value={provenance}
              onChange={(e) => setProvenance(e.target.value as ProvenanceType)}
            >
              <option value="user_provided">User Provided</option>
              <option value="imported">Imported</option>
              <option value="ai_enhanced">AI Enhanced</option>
              <option value="ai_generated">AI Generated</option>
            </SelectField>
          </div>

          {/* Linked Work Experiences */}
          {(profile.experiences || []).length > 0 && (
            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
              <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
                Used in Work Experiences (Relational Proof)
              </label>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {(profile.experiences || []).map((exp) => (
                  <label key={exp.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "#334155", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={selectedExpIds.includes(exp.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedExpIds([...selectedExpIds, exp.id]);
                        } else {
                          setSelectedExpIds(selectedExpIds.filter((id) => id !== exp.id));
                        }
                      }}
                    />
                    <span>{exp.company} — {exp.position}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Linked Projects */}
          {(profile.projects || []).length > 0 && (
            <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
              <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
                Used in Projects
              </label>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                {(profile.projects || []).map((proj) => (
                  <label key={proj.id} style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "#334155", cursor: "pointer" }}>
                    <input
                      type="checkbox"
                      checked={selectedProjIds.includes(proj.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedProjIds([...selectedProjIds, proj.id]);
                        } else {
                          setSelectedProjIds(selectedProjIds.filter((id) => id !== proj.id));
                        }
                      }}
                    />
                    <span>{proj.name}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Evidence References */}
          <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: "0.75rem" }}>
            <label className="field-label" style={{ display: "block", marginBottom: "0.375rem" }}>
              Evidence Sources & Citations (Optional)
            </label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem", marginBottom: "0.5rem" }}>
              {evidenceRefs.map((ref) => (
                <Badge key={ref} tone="green">
                  {ref}
                  <button
                    type="button"
                    onClick={() => handleRemoveRef(ref)}
                    style={{ marginLeft: "0.375rem", background: "none", border: "none", cursor: "pointer" }}
                    aria-label={`Remove ${ref}`}
                  >
                    <X size={12} aria-hidden="true" />
                  </button>
                </Badge>
              ))}
            </div>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <input
                className="input"
                placeholder="e.g. Voyago GitHub repo, Northstar design token library"
                value={newRef}
                onChange={(e) => setNewRef(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddRef(e);
                  }
                }}
              />
              <Button size="sm" variant="secondary" onClick={handleAddRef}>
                Add Citation
              </Button>
            </div>
          </div>
        </form>
      </Modal>
    </div>
  );
}
