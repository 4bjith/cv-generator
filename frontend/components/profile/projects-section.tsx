"use client";

import { useState } from "react";
import { Plus, Trash, PencilSimple, Code, GithubLogo, Globe, Star, ArrowUpRight, ShieldCheck } from "@phosphor-icons/react";
import { Badge, Button, Card, Field, IconButton, Modal, SelectField, TextareaField } from "@/components/ui";
import {
  useAddProject,
  useDeleteProject,
  useUpdateProject,
} from "@/hooks/use-profile";
import { CandidateProfileData, ProjectRecord, ProvenanceType } from "@/types/profile";

interface ProjectsSectionProps {
  profile: CandidateProfileData;
  onToast: (title: string, message: string, type?: "success" | "info" | "error") => void;
}

const PROVENANCE_TONES: Record<ProvenanceType, "neutral" | "blue" | "purple" | "amber"> = {
  user_provided: "neutral",
  imported: "blue",
  ai_enhanced: "purple",
  ai_generated: "amber",
};

export function ProjectsSection({ profile, onToast }: ProjectsSectionProps) {
  const [modalOpen, setModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<ProjectRecord | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [role, setRole] = useState("");
  const [description, setDescription] = useState("");
  const [problem, setProblem] = useState("");
  const [solution, setSolution] = useState("");
  const [architecture, setArchitecture] = useState("");
  const [responsibilitiesText, setResponsibilitiesText] = useState("");
  const [achievementsText, setAchievementsText] = useState("");
  const [technologiesText, setTechnologiesText] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [teamSize, setTeamSize] = useState("");
  const [liveUrl, setLiveUrl] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [provenance, setProvenance] = useState<ProvenanceType>("user_provided");
  const [featured, setFeatured] = useState(false);

  const addProjectMutation = useAddProject();
  const updateProjectMutation = useUpdateProject();
  const deleteProjectMutation = useDeleteProject();

  const handleOpenAdd = () => {
    setEditingProject(null);
    setName("");
    setRole("");
    setDescription("");
    setProblem("");
    setSolution("");
    setArchitecture("");
    setResponsibilitiesText("");
    setAchievementsText("");
    setTechnologiesText("");
    setStartDate("");
    setEndDate("");
    setTeamSize("");
    setLiveUrl("");
    setRepoUrl("");
    setProvenance("user_provided");
    setFeatured(false);
    setModalOpen(true);
  };

  const handleOpenEdit = (proj: ProjectRecord) => {
    setEditingProject(proj);
    setName(proj.name);
    setRole(proj.role || "");
    setDescription(proj.description || "");
    setProblem(proj.problem || "");
    setSolution(proj.solution || "");
    setArchitecture(proj.architecture || "");
    setResponsibilitiesText((proj.responsibilities || []).join("\n"));
    setAchievementsText((proj.achievements || []).join("\n"));
    setTechnologiesText((proj.technologies || []).join(", "));
    setStartDate(proj.start_date || "");
    setEndDate(proj.end_date || "");
    setTeamSize(proj.team_size?.toString() || "");
    setLiveUrl(proj.live_url || "");
    setRepoUrl(proj.repository_url || "");
    setProvenance(proj.provenance || "user_provided");
    setFeatured(proj.featured);
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      onToast("Project name required", "Please enter a project name.", "error");
      return;
    }

    if (startDate.trim() && endDate.trim() && endDate.trim() < startDate.trim()) {
      onToast("Invalid dates", "End date cannot precede start date.", "error");
      return;
    }

    const responsibilities = responsibilitiesText
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);

    const achievements = achievementsText
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);

    const technologies = technologiesText
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);

    const parsedTeam = teamSize.trim() ? parseInt(teamSize, 10) : undefined;

    try {
      if (editingProject) {
        await updateProjectMutation.mutateAsync({
          id: editingProject.id,
          payload: {
            name: name.trim(),
            role: role.trim() || undefined,
            description: description.trim() || undefined,
            problem: problem.trim() || undefined,
            solution: solution.trim() || undefined,
            architecture: architecture.trim() || undefined,
            responsibilities,
            achievements,
            technologies,
            start_date: startDate.trim() || undefined,
            end_date: endDate.trim() || undefined,
            team_size: parsedTeam,
            live_url: liveUrl.trim() || undefined,
            repository_url: repoUrl.trim() || undefined,
            provenance,
            featured,
          },
        });
        onToast("Project updated", `Saved ${name}.`, "success");
      } else {
        await addProjectMutation.mutateAsync({
          name: name.trim(),
          role: role.trim() || undefined,
          description: description.trim() || undefined,
          problem: problem.trim() || undefined,
          solution: solution.trim() || undefined,
          architecture: architecture.trim() || undefined,
          responsibilities,
          achievements,
          technologies,
          start_date: startDate.trim() || undefined,
          end_date: endDate.trim() || undefined,
          team_size: parsedTeam,
          live_url: liveUrl.trim() || undefined,
          repository_url: repoUrl.trim() || undefined,
          provenance,
          featured,
          order_index: (profile.projects?.length || 0),
        });
        onToast("Project added", `Added ${name}.`, "success");
      }
      setModalOpen(false);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to save project.";
      onToast("Save failed", msg, "error");
    }
  };

  const handleDelete = async (id: string, projName: string) => {
    try {
      await deleteProjectMutation.mutateAsync(id);
      onToast("Project deleted", `Removed ${projName}.`, "info");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to delete project.";
      onToast("Delete failed", msg, "error");
    }
  };

  const projects = profile.projects || [];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#09090b" }}>
            First-Class Projects & Technical Proof
          </h2>
          <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
            Detailed project records containing technical architecture, problem/solution narratives, and repository links.
          </p>
        </div>
        <Button icon={<Plus size={16} aria-hidden="true" />} onClick={handleOpenAdd}>
          Add Project
        </Button>
      </div>

      {projects.length > 0 ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.25rem" }}>
          {projects.map((proj) => {
            const evidenceCount = (proj.evidence_ids || []).length;
            return (
              <Card key={proj.id} style={{ padding: "1.75rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                    <div className="source-icon">
                      <Code size={18} aria-hidden="true" />
                    </div>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                        <h3 style={{ fontSize: "1.125rem", fontWeight: 700, color: "#09090b" }}>
                          {proj.name}
                        </h3>
                        {proj.featured && (
                          <Badge tone="purple">
                            <Star size={12} weight="fill" aria-hidden="true" /> Featured
                          </Badge>
                        )}
                        {proj.provenance && (
                          <Badge tone={PROVENANCE_TONES[proj.provenance] || "neutral"}>
                            {proj.provenance.replace(/_/g, " ")}
                          </Badge>
                        )}
                        {evidenceCount > 0 && (
                          <Badge tone="green">
                            <ShieldCheck size={12} style={{ display: "inline", marginRight: "0.25rem" }} />
                            {evidenceCount} Evidence Record{evidenceCount > 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>
                      {proj.role && (
                        <p style={{ fontSize: "0.8125rem", color: "#64748b", marginTop: "0.125rem" }}>
                          Role: <strong>{proj.role}</strong>
                          {proj.team_size ? ` · Team of ${proj.team_size}` : ""}
                        </p>
                      )}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "0.25rem" }}>
                    <IconButton label={`Edit ${proj.name}`} onClick={() => handleOpenEdit(proj)}>
                      <PencilSimple size={16} aria-hidden="true" />
                    </IconButton>
                    <IconButton label={`Delete ${proj.name}`} onClick={() => handleDelete(proj.id, proj.name)}>
                      <Trash size={16} aria-hidden="true" />
                    </IconButton>
                  </div>
                </div>

                {proj.description && (
                  <p style={{ fontSize: "0.875rem", color: "#334155", lineHeight: 1.5 }}>
                    {proj.description}
                  </p>
                )}

                {(proj.problem || proj.solution) && (
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", backgroundColor: "#f8fafc", padding: "1rem", borderRadius: "0.75rem", border: "1px solid #e2e8f0" }}>
                    {proj.problem && (
                      <div>
                        <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#b45309", textTransform: "uppercase" }}>
                          Problem Statement
                        </p>
                        <p style={{ fontSize: "0.8125rem", color: "#475569", marginTop: "0.25rem" }}>
                          {proj.problem}
                        </p>
                      </div>
                    )}
                    {proj.solution && (
                      <div>
                        <p style={{ fontSize: "0.75rem", fontWeight: 700, color: "#047857", textTransform: "uppercase" }}>
                          Technical Solution
                        </p>
                        <p style={{ fontSize: "0.8125rem", color: "#475569", marginTop: "0.25rem" }}>
                          {proj.solution}
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {proj.architecture && (
                  <div style={{ fontSize: "0.8125rem", color: "#475569" }}>
                    <strong style={{ color: "#09090b" }}>Architecture:</strong> {proj.architecture}
                  </div>
                )}

                {proj.technologies && proj.technologies.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.375rem" }}>
                    {proj.technologies.map((tech) => (
                      <Badge key={tech} tone="neutral">
                        {tech}
                      </Badge>
                    ))}
                  </div>
                )}

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderTop: "1px solid #f1f5f9", paddingTop: "0.75rem", marginTop: "0.25rem" }}>
                  <div style={{ display: "flex", gap: "1rem", fontSize: "0.8125rem" }}>
                    {proj.repository_url && (
                      <a
                        href={proj.repository_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", color: "#2563eb" }}
                      >
                        <GithubLogo size={16} aria-hidden="true" /> Code Repository <ArrowUpRight size={13} aria-hidden="true" />
                      </a>
                    )}
                    {proj.live_url && (
                      <a
                        href={proj.live_url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", color: "#059669" }}
                      >
                        <Globe size={16} aria-hidden="true" /> Live Demo <ArrowUpRight size={13} aria-hidden="true" />
                      </a>
                    )}
                  </div>
                  {(proj.start_date || proj.end_date) && (
                    <span style={{ fontSize: "0.75rem", color: "#64748b" }}>
                      {proj.start_date || "—"} to {proj.end_date || "Present"}
                    </span>
                  )}
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
              No projects added
            </h3>
            <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
              Add personal, open-source, or commercial projects to provide solid technical evidence for future applications.
            </p>
          </div>
          <Button onClick={handleOpenAdd} icon={<Plus size={16} aria-hidden="true" />}>
            Add First Project
          </Button>
        </Card>
      )}

      {/* Project Modal */}
      <Modal
        open={modalOpen}
        title={editingProject ? "Edit Project" : "Add Project"}
        description="Add a verified project with problem/solution context and stack."
        onClose={() => setModalOpen(false)}
        footer={
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem" }}>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              loading={addProjectMutation.isPending || updateProjectMutation.isPending}
            >
              {editingProject ? "Save Changes" : "Save Project"}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem", maxHeight: "70vh", overflowY: "auto", paddingRight: "0.25rem" }}>
          <div className="profile-form-grid">
            <Field
              label="Project Name *"
              name="project_name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Voyago, Real-time Engine"
              required
            />
            <Field
              label="Your Role in Project"
              name="project_role"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Lead Architect, Core Contributor"
            />
            <Field
              label="Repository URL"
              name="repo_url"
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/username/project"
            />
            <Field
              label="Live Demo URL"
              name="live_url"
              type="url"
              value={liveUrl}
              onChange={(e) => setLiveUrl(e.target.value)}
              placeholder="https://project.app"
            />
            <Field
              label="Start Date"
              name="project_start"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              placeholder="YYYY-MM (e.g. 2023-01)"
            />
            <Field
              label="End Date"
              name="project_end"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              placeholder="YYYY-MM or Present"
            />
            <Field
              label="Team Size"
              name="team_size"
              type="number"
              min="1"
              value={teamSize}
              onChange={(e) => setTeamSize(e.target.value)}
              placeholder="e.g. 4"
            />
            <SelectField
              label="Provenance (Origin)"
              name="project_provenance"
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
              checked={featured}
              onChange={(e) => setFeatured(e.target.checked)}
            />
            <span>Feature this project prominently</span>
          </label>

          <TextareaField
            label="Project Description"
            name="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="High-level overview of what this project does and why it was built..."
            rows={3}
          />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <TextareaField
              label="Problem Addressed"
              name="problem"
              value={problem}
              onChange={(e) => setProblem(e.target.value)}
              placeholder="What pain point or engineering challenge did this solve?"
              rows={3}
            />
            <TextareaField
              label="Solution Implemented"
              name="solution"
              value={solution}
              onChange={(e) => setSolution(e.target.value)}
              placeholder="How was the problem solved technically?"
              rows={3}
            />
          </div>

          <TextareaField
            label="Technical Architecture"
            name="architecture"
            value={architecture}
            onChange={(e) => setArchitecture(e.target.value)}
            placeholder="e.g. Microservices with Event-driven Redis Pub/Sub and Next.js SSR"
            rows={2}
          />

          <Field
            label="Technologies Used (comma-separated)"
            name="technologies"
            value={technologiesText}
            onChange={(e) => setTechnologiesText(e.target.value)}
            placeholder="Next.js, TypeScript, PostgreSQL, Docker, Redis"
          />
        </form>
      </Modal>
    </div>
  );
}
